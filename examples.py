"""
FΦRS33 V3.1 - Complete Examples
All examples in one file for easy reference

V3.1 Features:
- Enhanced predictive algorithms
- Intelligent optimization strategies
- Circuit-aware analysis
- Real-time hardware insights
"""

import os
from qiskit import QuantumCircuit
from fors33 import Optimizer

# ============================================================================
# SETUP - Get your API keys first!
# ============================================================================

# Get from https://quantum.ibm.com/
IBM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")

# Get from https://api.fors33.com/register (Free tier: 50 credits/month)
# V3.1: Backward compatible with V1.2 API
FORS33_KEY = os.getenv("FORS33_API_KEY")

if not IBM_TOKEN or not FORS33_KEY:
    print("❌ Set environment variables:")
    print("   export IBM_QUANTUM_TOKEN='your_token'")
    print("   export FORS33_API_KEY='your_key'")
    exit(1)

# Initialize optimizer
opt = Optimizer(ibm_token=IBM_TOKEN, fors33_api_key=FORS33_KEY)

# ============================================================================
# EXAMPLE 1: Simple Recommendation (0.5 credits)
# ============================================================================

print("\n" + "="*70)
print("EXAMPLE 1: Get Circuit-Aware Recommendation")
print("="*70)

# Get optimal qubits for VQE circuit
rec = opt.get_recommendation(
    circuit_type="vqe",  # Dense connectivity needed
    n_qubits=5,
    backend="auto"  # Auto-select best QPU
)

print(f"✅ Optimal qubits: {rec['qubits']}")
print(f"✅ Backend: {rec['backend']}")
print(f"✅ Avg fidelity: {rec['avg_fidelity']*100:.1f}%")
print(f"💳 Credits used: 0.5")

# ============================================================================
# EXAMPLE 2: VQE Circuit Optimization (1 credit)
# ============================================================================

print("\n" + "="*70)
print("EXAMPLE 2: VQE Circuit with Holistic Optimization")
print("="*70)

# Create VQE-like circuit
vqe_circuit = QuantumCircuit(5)
vqe_circuit.h(range(5))
for i in range(4):
    vqe_circuit.cx(i, i+1)
vqe_circuit.measure_all()

# Run with circuit-aware optimization
job = opt.run_optimized(
    circuit=vqe_circuit,
    circuit_type="vqe",  # Dense connectivity
    backend="auto",
    shots=1000
)

print(f"✅ Job submitted: {job.job_id()}")
print(f"🔗 Monitor: https://quantum.ibm.com/jobs/{job.job_id()}")
print(f"💳 Credits used: 1")

# ============================================================================
# EXAMPLE 3: QAOA Circuit (1 credit)
# ============================================================================

print("\n" + "="*70)
print("EXAMPLE 3: QAOA Circuit Optimization")
print("="*70)

# Create QAOA-like circuit
qaoa_circuit = QuantumCircuit(10)
qaoa_circuit.h(range(10))
for i in range(10):
    qaoa_circuit.rz(0.1, i)
for i in range(9):
    qaoa_circuit.cx(i, i+1)
qaoa_circuit.cx(9, 0)  # Ring connectivity
qaoa_circuit.measure_all()

# Get recommendation for QAOA
qaoa_rec = opt.get_recommendation(circuit_type="qaoa", n_qubits=10)
print(f"✅ QAOA optimal qubits: {qaoa_rec['qubits']}")
print(f"💳 Credits used: 0.5")

# ============================================================================
# EXAMPLE 4: Repetition Code (Built-in Profiles)
# ============================================================================

print("\n" + "="*70)
print("EXAMPLE 4: Built-in Velocity Profile (Repetition Code)")
print("="*70)

# Use built-in Velocity profile (Line topology @ 700dt)
velocity_job = opt.run_optimized(
    circuit_type="repetition",
    backend="ibm_fez",
    shots=500
)

print(f"✅ Velocity job: {velocity_job.job_id()}")
print(f"📊 Expected fidelity: 85.0%")
print(f"💳 Credits used: 1")

# ============================================================================
# EXAMPLE 5: Check Your Credit Balance
# ============================================================================

print("\n" + "="*70)
print("EXAMPLE 5: Monitor Your Usage")
print("="*70)

# Check remaining credits
balance = opt.get_credit_balance()
print(f"💳 Credits remaining: {balance}")

# Get usage statistics
usage = opt.get_usage_stats()
print(f"📊 Jobs submitted: {usage['jobs']}")
print(f"📊 Credits used: {usage['credits']}")
print(f"📊 Success rate: {usage['success_rate']}%")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("EXAMPLES COMPLETE!")
print("="*70)
print(f"""
✅ All examples ran successfully!

💡 Key Takeaways:
   - Use get_recommendation() for 0.5 credits (no job submission)
   - Use run_optimized() for 1 credit (full job submission)
   - Circuit-aware selection improves performance
   - Free tier: 50 credits/month = 50 jobs or 100 recommendations
   - V3.1: Acceleration-based Φ predicts failures before they happen

🚀 Next Steps:
   1. Run your own circuits with circuit_type parameter
   2. Monitor your credit usage
   3. Upgrade when ready: https://api.fors33.com/billing

📚 Documentation: https://docs.fors33.com
💬 Community: https://discord.gg/fors33
""")
