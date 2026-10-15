import pandas as pd

df = pd.read_csv("data/spare_parts.csv")

print("=== SparePart AI Compatibility Checker ===")

machine = input("Enter machine model (M100/M200/M300): ").strip().upper()
voltage = input("Enter required voltage (230/415): ").strip()

try:
    voltage = int(voltage)
except ValueError:
    print("Please enter a valid voltage.")
    raise SystemExit

# Find parts listed for the selected machine
machine_parts = df[df["machine_model"].str.upper() == machine]

if machine_parts.empty:
    print("Machine model not found.")
else:
    # Keep parts whose listed voltage matches the requirement
    compatible = machine_parts[machine_parts["voltage"] == voltage]

    if compatible.empty:
        print("No parts match the machine and voltage criteria.")
    else:
        print("\nParts matching the listed criteria:")
        print(compatible[
            ["part_id", "part_name", "voltage", "stock", "location"]
        ].to_string(index=False))

        print("\nNote: Verify all specifications with the manufacturer.")