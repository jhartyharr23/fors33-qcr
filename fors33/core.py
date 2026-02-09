"""FΦRS33 V1.2 - Clean Core Module"""

from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import requests
import os
from typing import Optional, Dict


class FORS33Client:
    """Client for FΦRS33 Telemetry API."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: str = "https://api.fors33.com"):
        self.api_key = api_key or os.getenv('FORS33_API_KEY')
        self.api_url = api_url.rstrip('/')
        
        if not self.api_key:
            raise ValueError(
                "FORS33 API key required. Get free key at: https://api.fors33.com/register"
            )
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_recommendation(self, backend: str = 'auto', num_qubits: int = 3, 
                          circuit_type: str = 'custom') -> Dict:
        """Get optimal qubit recommendation."""
        url = f"{self.api_url}/api/v1/recommendation"
        params = {'backend': backend, 'num_qubits': num_qubits, 'circuit_type': circuit_type}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
    
    def get_usage(self) -> Dict:
        """Get API usage statistics."""
        url = f"{self.api_url}/api/v1/usage"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get usage: {e}")


class Optimizer:
    """FΦRS33 V3.1 Quantum Optimizer with acceleration-based predictive error mitigation."""
    
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
    
    def get_recommendation(self, circuit_type: str = "custom", n_qubits: int = 3, 
                          backend: str = "auto") -> Dict:
        """
        Get V3.1 circuit-aware recommendation with acceleration-based optimization.
        
        Args:
            circuit_type: 'vqe', 'qaoa', 'repetition', or 'custom'
            n_qubits: Number of data qubits needed
            backend: Backend name or 'auto'
        
        Returns:
            Dict with qubits, backend, fidelity_score, etc.
        """
        return self.client.get_recommendation(
            backend=backend, 
            num_qubits=n_qubits, 
            circuit_type=circuit_type
        )
    
    def run_optimized(self, circuit_type: str = "custom", backend: str = "auto", 
                     shots: int = 1000) -> object:
        """
        Execute optimized quantum job.
        
        Args:
            circuit_type: Type of circuit for optimization
            backend: Target backend or 'auto'
            shots: Number of execution shots
        
        Returns:
            Qiskit Runtime job object
        """
        from .circuits import build_velocity_circuit
        
        # Get recommendation
        rec = self.get_recommendation(circuit_type=circuit_type, n_qubits=3, backend=backend)
        
        selected_backend = rec['backend']
        qubits = rec['qubits']
        
        # Get backend
        backend_obj = self.service.backend(selected_backend)
        
        # Build and transpile circuit
        qc = build_velocity_circuit()
        t_qc = transpile(qc, backend_obj, initial_layout=qubits, optimization_level=3)
        
        # Run
        sampler = Sampler(mode=backend_obj)
        job = sampler.run([t_qc], shots=shots)
        
        return job
    
    def get_usage(self) -> Dict:
        """Get API usage statistics."""
        return self.client.get_usage()
