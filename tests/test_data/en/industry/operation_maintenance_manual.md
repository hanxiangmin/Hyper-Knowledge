# Automated Assembly Line A1 Operation and Maintenance Manual

**Document Number**: OMM-2024-001
**Version**: v2.5
**Preparation Date**: March 2024
**Applicable Equipment**: Automated Assembly Line A1

---

## Part 1: Equipment Operation

### Chapter 1: Scope of Application

This procedure applies to the startup operation and operation management of Automated Assembly Line A1, including CNC machining centers, robot arm systems, material handling systems, and quality inspection stations.

---

### Chapter 2: Startup Operation Procedure

#### 2.1 Pre-Startup Inspection

**Environmental Inspection**:
- Temperature: Ambient temperature should be within 15-30°C
- Humidity: Relative humidity should be within 40-70%
- Cleanliness: No debris or water accumulation around equipment

**Equipment Inspection**:
- Power: Main power voltage normal, three-phase balanced
- Air Source: Air pressure maintained at 0.5-0.7 MPa
- Lubrication: All lubrication points have sufficient grease
- Safety Devices: Emergency stop button, protective door lock normal

#### 2.2 Startup Steps

**Step 1: Enable Auxiliary Systems**
- Operation: Turn on control cabinet auxiliary power
- Steps: Open control cabinet door → Close auxiliary power switch → Confirm auxiliary power indicator light is on
- Expected Result: Auxiliary power normally connected, control panel shows ready status
- Trigger Condition: Auxiliary power normal

**Step 2: Start Hydraulic System**
- Operation: Start hydraulic station
- Steps: Press hydraulic station start button → Wait for hydraulic pressure to rise to set value → Check: Hydraulic pressure stable at 3.5 MPa, oil level normal
- Expected Result: Hydraulic pressure stable at 3.5 MPa, oil level normal
- Trigger Condition: Hydraulic pressure reaches set value

**Step 3: Start Cooling System**
- Operation: Turn on cooling pump
- Steps: Turn on cooling pump power switch → Adjust coolant flow rate → Check coolant temperature
- Expected Result: Cooling system operates normally, inlet-outlet temperature difference is 5-10°C
- Trigger Condition: Cooling pump operates without abnormality

**Step 4: Start Control System**
- Operation: Start main control system
- Steps: Select "Auto Mode" on HMI → Click "System Start" button → Wait for system self-check to complete
- Expected Result: HMI displays "System Ready," no alarm information
- Trigger Condition: System self-check passed

**Step 5: Activate Servo System**
- Operation: Start servo drive
- Steps: Start each axis servo drive in sequence → Wait for servo system to be ready → Execute origin return
- Expected Result: Each axis returns to reference origin, position display correct
- Trigger Condition: Servo system has no faults

**Step 6: Start Material Handling System**
- Operation: Turn on conveyor and AGV
- Steps: Start conveyor motor → Activate AGV navigation system → Set transport path
- Expected Result: Conveyor operates normally, AGV in position on standby
- Trigger Condition: Conveyor operates smoothly

**Step 7: Start Robot System**
- Operation: Activate robot arm
- Steps: Start robot arm control cabinet → Load processing program → Execute robot arm origin return
- Expected Result: All robot arm joints normal, arriving at origin position
- Trigger Condition: Robot arm has no collision alarm

**Step 8: Start Quality Inspection System**
- Operation: Turn on inspection equipment
- Steps: Start vision inspection system → Calibrate inspection parameters → Load inspection program
- Expected Result: Inspection system ready, can normally identify workpieces
