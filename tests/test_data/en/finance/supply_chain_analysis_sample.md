# New Energy Vehicle Supply Chain Risk Assessment Report

**Prepared by**: Deloitte Consulting (Shanghai) Co., Ltd.
**Client**: Auric New Energy Vehicle Technology Co., Ltd.
**Report Date**: November 2025
**Classification**: Confidential — For Client Internal Use Only

---

## Executive Summary

This report provides a comprehensive risk assessment of the core component supply chain for Auric New Energy Vehicle Technology Co., Ltd. (hereinafter referred to as "Auric" or "the Company"). The assessment scope covers 38 Tier-1 suppliers, 96 Tier-2 suppliers, and key raw material supply sources, involving 12 countries and regions. The report identifies 6 high-risk supply chain nodes and provides mitigation recommendations for each risk.

---

## Supply Chain Architecture

### 2.1 Core Component Tier-1 Suppliers

#### Power Battery

| Supplier | Location | Supply Product | Annual Procurement (RMB billion) | Supply Share | Risk Level |
|---|---|---|---|---|---|
| **CATL** | Ningde, Fujian | Ternary lithium/P lithium battery packs | 4.85 | 58% | Medium |
| **BYD FinDreams Battery** | Chongqing | Blade battery packs | 2.20 | 26% | Low |
| **CALB** | Changzhou, Jiangsu | Ternary lithium (backup supplier) | 1.35 | 16% | Medium |

#### Electric Drive System

| Supplier | Location | Supply Product | Annual Procurement (RMB billion) | Supply Share | Risk Level |
|---|---|---|---|---|---|
| **Inovance** | Shenzhen, Guangdong | Permanent magnet synchronous motors, motor controllers | 1.82 | 52% | Medium |
| **Nidec** | Kyoto, Japan | Drive motor assembly (E-Axle) | 1.25 | 36% | High |
| **JJE** | Beijing | Hybrid electric motors | 0.42 | 12% | Low |

#### Intelligent Driving Chips

| Supplier | Location | Supply Product | Annual Procurement (RMB billion) | Supply Share | Risk Level |
|---|---|---|---|---|---|
| **NVIDIA** | Santa Clara, CA | Orin X intelligent driving SoC | 0.86 | 65% | High |
| **Horizon Robotics** | Beijing | Journey 5 chip | 0.32 | 24% | Medium |
| **Black Sesame** | Shanghai | A1000 Pro chip | 0.15 | 11% | Medium |

#### Body and Chassis

| Supplier | Location | Supply Product | Annual Procurement (RMB billion) | Risk Level |
|---|---|---|---|---|
| **Tuopu Group** | Ningbo, Zhejiang | Chassis suspension systems, lightweight components | 0.68 | Low |
| **Zhongding** | Ningguo, Anhui | Rubber seals, fluid piping | 0.35 | Low |
| **Fuyao Glass** | Fuqing, Fujian | Automotive glass, HUD抬头显示玻璃 | 0.42 | Low |
| **Joyson Electronic** | Ningbo, Zhejiang | Safety systems (airbags, steering wheels) | 0.51 | Medium |

#### Cabin and Connected Vehicle

| Supplier | Location | Supply Product | Annual Procurement (RMB billion) | Risk Level |
|---|---|---|---|---|
| **Qualcomm** | San Diego, CA | 8295 cabin chip | 0.48 | High |
| **Desay SV** | Huizhou, Guangdong | Intelligent cockpit domain controller | 0.56 | Medium |
| **BOE** | Beijing | Vehicle display screens | 0.32 | Low |

---

### 2.2 Tier-2 Supplier Key Dependencies

**Lithium Battery Key Raw Materials**

- **Tianqi Lithium** (Shehong, Sichuan) → Supplies battery-grade lithium carbonate to CATL. Tianqi controls approximately 10% of global lithium ore resources, and its Greenbushes mine in Australia is the world's largest hard rock lithium mine. Lithium carbonate price has fallen from RMB 600,000/ton at the 2022 peak to approximately RMB 80,000/ton, but supply-side concentration risk remains.

- **Huayou Cobalt** (Tongxiang, Zhejiang) → Supplies battery-grade cobalt sulfate and precursors to CATL and CALB. Cobalt resources are 70% from DRC, with geopolitical risk and ESG compliance risk.

- **GEM** (Jingmen, Hubei) → Battery recycling and precursor materials. The company is China's largest power battery recycling enterprise with recycling capacity of 300,000 tons/year, helping reduce dependence on upstream mineral resources.

**Semiconductor Manufacturing Chain**

- **TSMC** (Hsinchu, Taiwan) → Manufactures intelligent driving/cabin chips for NVIDIA and Qualcomm on behalf. NVIDIA Orin X chip uses Samsung 8nm process, but next-generation Thor chip will move to TSMC 5nm. Qualcomm 8295 uses TSMC 5nm process. TSMC is an irreplaceable key node in the intelligent driving chip supply chain.

- **ASE** (Kaohsiung, Taiwan) → Provides advanced packaging services for NVIDIA and Qualcomm. Packaging is currently one of the most capacity-constrained segments in the chip supply chain.

**Rare Earth Permanent Magnet Materials**

- **Northern Rare Earth** (Baotou, Inner Mongolia) → Supplies NdFeB permanent magnet materials to Inovance and Nidec for manufacturing permanent magnets in drive motors. China controls approximately 60% of global rare earth minerals and 90% of rare earth processing capacity. Since 2025, rare earth export control policies have tightened.

---

## Risk Assessment

### 3.1 Geopolitical Risk — Extremely High

**US-China Tech Competition and Chip Controls**

The largest geopolitical risk in Auric's supply chain comes from US-China tech decoupling. The Company has high dependence on US-based chips:

- NVIDIA Orin X intelligent driving chip: accounts for 100% chip supply for the Company's advanced intelligent driving solutions, with annual procurement of RMB 86 million
- Qualcomm 8295 cabin chip: accounts for 80% chip supply for the Company's mid-to-high-end cabin solutions, with annual procurement of RMB 48 million

**Risk Assessment**: The US Department of Commerce has upgraded chip export controls to China multiple times in 2022 and 2023. While current controls primarily target advanced AI training chips, there is no guarantee that automotive high-computing chips will not be included in the control list in the future. Once NVIDIA and Qualcomm chips are prohibited from exporting to China, the Company's advanced intelligent driving and cabin system production will face production stoppage risk after existing inventory is exhausted (approximately 4-6 months).

**Mitigation Measures**:
1. Accelerate adaptation and validation work for Horizon Robotics Journey 6 chip, planned to complete full model adaptation by Q3 2026 (expected investment of RMB 120 million)
2. Initiate cooperation evaluation with Huawei MDC intelligent driving platform
