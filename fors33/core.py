"""FΦRS33 - Quantum Circuit Optimizer SDK"""

from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import requests
import os
from typing import Optional, Dict


class FORS33Client:
    """Client for FΦRS33 Telemetry API."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: str = "https://fors33.com"):
        self.api_key = api_key or os.getenv('FORS33_API_KEY')
        self.api_url = api_url.rstrip('/')
        
        if not self.api_key:
            raise ValueError(
                "FORS33 API key required. Get your key at: https://fors33.com/quantum/qcr/api-keys"
            )
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_recommendation(self, backend: str = 'auto', num_qubits: int = None,
                          data_qubits: int = None, ancilla_qubits: int = 0,
                          circuit_type: str = 'custom') -> Dict:
        """Get optimal qubit recommendation.
        
        Args:
            backend: Backend name or 'auto'
            data_qubits: Number of data qubits in your circuit
            ancilla_qubits: Number of ancilla/syndrome qubits (default: 0)
            num_qubits: Total qubits (backward compat, used if data_qubits not set)
            circuit_type: 'vqe', 'qaoa', 'repetition', or 'custom'
        
        Returns:
            Dict with data_qubits, ancilla_qubits, qubits (combined layout),
            fidelity_score, confidence, etc.
        """
        url = f"{self.api_url}/api/v1/recommendation"
        
        if data_qubits is not None:
            params = {'backend': backend, 'data_qubits': data_qubits,
                      'ancilla_qubits': ancilla_qubits, 'circuit_type': circuit_type}
        else:
            params = {'backend': backend, 'num_qubits': num_qubits or 3,
                      'circuit_type': circuit_type}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
    
    def get_usage(self) -> Dict:
        """Get API usage statistics."""
        url = f"{self.api_url}/api/v1/usage"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get usage: {e}")


class Optimizer:
    """FΦRS33 V3.1 Quantum Circuit Optimizer."""
    
    def __init__(self, ibm_token: str, fors33_api_key: Optional[str] = None):
        """
        Initialize the FΦRS33 V3.1 Optimizer.
        
        Args:
            ibm_token: IBM Quantum API token
            fors33_api_key: FΦRS33 API key (optional, checks FORS33_API_KEY env var)
        """
        self.service = QiskitRuntimeService(token=ibm_token)
        self.client = FORS33Client(api_key=fors33_api_key)
        self.version = "3.1.0"
    
    def get_recommendation(self, circuit_type: str = "custom", 
                          data_qubits: int = 3, ancilla_qubits: int = 0,
                          backend: str = "auto") -> Dict:
        """
        Get V3.1 circuit-aware recommendation.
        
        Args:
            circuit_type: 'vqe', 'qaoa', 'repetition', or 'custom'
            data_qubits: Number of data qubits in your circuit
            ancilla_qubits: Number of ancilla/syndrome qubits (default: 0)
            backend: Backend name or 'auto'
        
        Returns:
            Dict with data_qubits, ancilla_qubits, qubits (combined layout),
            fidelity_score, confidence, etc.
        """
        return self.client.get_recommendation(
            backend=backend,
            data_qubits=data_qubits,
            ancilla_qubits=ancilla_qubits,
            circuit_type=circuit_type
        )
    
    def run_optimized(self, circuit, circuit_type: str = "custom", 
                     backend: str = "auto", data_qubits: Optional[int] = None,
                     ancilla_qubits: Optional[int] = None,
                     shots: int = 1000) -> object:
        """
        Transpile and execute a circuit using FΦRS33 optimized qubit selection.
        
        Args:
            circuit: Your QuantumCircuit to optimize and run
            circuit_type: 'vqe', 'qaoa', 'repetition', or 'custom'
            backend: Target backend or 'auto'
            data_qubits: Number of data qubits (auto-detected from circuit if omitted)
            ancilla_qubits: Number of ancilla qubits (default: 0)
            shots: Number of execution shots
        
        Returns:
            Qiskit Runtime job object
        """
        # Auto-detect from circuit if not specified
        if data_qubits is None:
            data_qubits = circuit.num_qubits
            ancilla_qubits = 0
        elif ancilla_qubits is None:
            ancilla_qubits = 0
        
        # Get optimal qubit layout from FΦRS33 API
        rec = self.get_recommendation(
            circuit_type=circuit_type, data_qubits=data_qubits,
            ancilla_qubits=ancilla_qubits, backend=backend
        )
        
        selected_backend = rec['backend']
        qubits = rec['qubits']
        
        # Get backend and transpile with our recommended layout
        backend_obj = self.service.backend(selected_backend)
        t_qc = transpile(circuit, backend_obj, initial_layout=qubits, optimization_level=3)
        
        # Execute
        sampler = Sampler(mode=backend_obj)
        job = sampler.run([t_qc], shots=shots)
        
        return job
    
    def get_usage(self) -> Dict:
        """Get API usage statistics."""
        return self.client.get_usage()
