# Industry Templates

Industrial documentation and operational analysis.

---

## Overview

Industry templates are designed for extracting information from industrial documentation, including equipment specifications, safety procedures, and operational workflows.

---

## Templates

### equipment_topology

**Type**: graph

**Purpose**: Extract equipment connections and topology

**Best for**:
- System diagrams
- P&IDs (Piping and Instrumentation Diagrams)
- Equipment manuals
- Network layouts

**Entities**:

- Equipment (pumps, valves, tanks, etc.)
- Sensors
- Control systems

**Relations**:

- `connected_to` — Physical connections
- `controlled_by` — Control relationships
- `monitors` — Monitoring relationships

=== "CLI"

    ```bash
    hk parse system_diagram.md -t industry/equipment_topology -l en
    ```

=== "Python"

    ```python
    ka = Template.create("industry/equipment_topology", "en")
    result = ka.parse(pandid_description)

    # Build index for interactive search/chat in visualization
    result.build_index()

    result.show()  # Shows equipment network with interactive features
    ```

---

### safety_control

**Type**: graph

**Purpose**: Extract safety control systems

**Best for**:
- Safety manuals
- HAZOP studies
- Safety system designs
- Emergency procedures

**Entities**:

- Safety functions
- Hazards
- Safeguards
- Sensors
- Actuators

**Relations**:

- `protects_against` — Safeguard-hazard relationship
- `triggers` — Sensor-action relationship
- `implements` — System-function relationship

=== "CLI"

    ```bash
    hk parse safety_manual.md -t industry/safety_control -l en
    ```

=== "Python"

    ```python
    ka = Template.create("industry/safety_control", "en")
    result = ka.parse(safety_text)

    print(f"Safety functions: {len(result.nodes)}")
    print(f"Protections: {len(result.edges)}")

    # Visualize safety system
    result.build_index()
    result.show()
    ```

---

### operation_flow

**Type**: graph

**Purpose**: Extract operational procedures

**Best for**:
- Operating procedures (SOPs)
- Batch records
- Process descriptions
- Work instructions

**Features**:

- Step sequences
- Decision points
- Parallel operations
- Dependencies

=== "CLI"

    ```bash
    hk parse sop.md -t industry/operation_flow -l en
    ```

=== "Python"

    ```python
    ka = Template.create("industry/operation_flow", "en")
    result = ka.parse(sop_text)

    print(f"Steps: {len(result.nodes)}")
    print(f"Flow connections: {len(result.edges)}")

    # Visualize operational workflow
    result.build_index()
    result.show()
    ```

---

### emergency_response

**Type**: graph

**Purpose**: Extract emergency response procedures

**Best for**:
- Emergency response plans
- Incident response guides
- Crisis management protocols

**Entities**:

- Emergency types
- Response actions
- Responsible parties
- Resources

**Relations**:

- `responds_to` — Action-emergency relationship
- `requires` — Resource requirements
- `notifies` — Notification chain

=== "CLI"

    ```bash
    hk parse emergency_plan.md -t industry/emergency_response -l en
    ```

=== "Python"

    ```python
    ka = Template.create("industry/emergency_response", "en")
    result = ka.parse(emergency_text)

    print(f"Emergency types: {len(result.nodes)}")
    print(f"Response actions: {len(result.edges)}")

    # Visualize emergency response plan
    result.build_index()
    result.show()
    ```

---

### failure_case

**Type**: temporal_graph

**Purpose**: Extract failure analysis cases

**Best for**:
- Root cause analysis reports
- Incident investigations
- Failure mode documentation

**Features**:

- Timeline of events
- Contributing factors
- Root causes
- Corrective actions

=== "CLI"

    ```bash
    hk parse incident_report.md -t industry/failure_case -l en
    ```

=== "Python"

    ```python
    ka = Template.create("industry/failure_case", "en")
    result = ka.parse(incident_text)

    print(f"Events: {len(result.nodes)}")
    for edge in result.edges:
        if hasattr(edge, 'time'):
            print(f"  {edge.time}: {edge.source} -> {edge.target}")

    # Visualize failure timeline
    result.build_index()
    result.show()
    ```

---

## Use Cases

### System Documentation

```python
from hyperknowledge import Template

ka = Template.create("industry/equipment_topology", "en")
system = ka.parse(pandid_description)

# Find all pumps
pumps = [e for e in system.data.entities if "pump" in e.type.lower()]

for pump in pumps:
    # Find connections
    connections = [
        r for r in system.data.relations
        if r.source == pump.name or r.target == pump.name
    ]
    print(f"{pump.name}: {len(connections)} connections")
```

### Safety Analysis

```python
ka = Template.create("industry/safety_control", "en")
safety = ka.parse(hazop_report)

# Map hazards to safeguards
hazards = [e for e in safety.data.entities if e.type == "hazard"]

for hazard in hazards:
    safeguards = [
        r.source for r in safety.data.relations
        if r.target == hazard.name and r.type == "protects_against"
    ]
    print(f"{hazard.name}:")
    for sg in safeguards:
        print(f"  Protected by: {sg}")
```

### Procedure Documentation

```python
ka = Template.create("industry/operation_flow", "en")
procedure = ka.parse(sop_document)

# Build index for interactive visualization
procedure.build_index()

# Visualize workflow with search/chat capabilities
procedure.show()

# Search for specific steps
results = procedure.search("startup sequence")
```

---

## Tips

1. **equipment_topology for system design** — Document equipment networks
2. **safety_control for HAZOP** — Extract safety systems
3. **operation_flow for SOPs** — Document procedures
4. **failure_case for RCA** — Analyze incidents

---

## See Also

- [Template Overview](overview.md)
- [General Templates](general.md)
