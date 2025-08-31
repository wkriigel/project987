# New File Structure and Outputs - One Option Per File

## 📁 **Complete File Structure**

```
x987/options/
├── __init__.py                    # Package initialization
├── base.py                        # Base classes (legacy, not used in new system)
├── detector.py                    # Main detection engine
├── registry.py                    # Auto-discovery registry
├── sport_chrono.py               # Sport Chrono Package Plus
├── pasm.py                       # PASM (Porsche Active Suspension Management)
├── limited_slip_differential.py  # Limited Slip Differential (LSD)
├── sport_exhaust.py              # Sport Exhaust (PSE)
├── sport_seats.py                # Sport Seats / Adaptive Sport Seats
├── heated_seats.py               # Heated Seats
├── bose_surround_sound.py        # BOSE Surround Sound
├── pcm_navigation.py             # PCM w/ Navigation
├── bi_xenon_headlights.py        # Bi-Xenon Headlights with Dynamic Cornering
├── upgraded_wheels.py            # 18–19" Upgraded Wheels
└── park_assist.py                # Park Assist
```

## 🔍 **Auto-Discovery Results**

The registry automatically discovers all 11 options:

```
✓ Discovered option: Bi-Xenon Headlights with Dynamic Cornering
✓ Discovered option: BOSE Surround Sound
✓ Discovered option: Heated Seats
✓ Discovered option: Limited Slip Differential (LSD)
✓ Discovered option: Park Assist
✓ Discovered option: PASM
✓ Discovered option: PCM w/ Navigation
✓ Discovered option: Sport Chrono Package Plus
✓ Discovered option: Sport Exhaust (PSE)
✓ Discovered option: Sport Seats / Adaptive Sport Seats
✓ Discovered option: 18–19" Upgraded Wheels

📋 Total options discovered: 11
```

## 📊 **Option File Outputs When Options Are Found**

| Option File | Option ID | Display Name | Category | Value | Is Present | Value When Present |
|-------------|-----------|--------------|----------|-------|------------|-------------------|
| `sport_chrono.py` | 639/640 | Sport Chrono Package Plus | performance | $0 | ✅ Yes | $1,000 |
| `pasm.py` | PASM | PASM | performance | $0 | ✅ Yes | $800 |
| `limited_slip_differential.py` | LSD | Limited Slip Differential (LSD) | performance | $0 | ✅ Yes | $1,200 |
| `sport_exhaust.py` | PSE | Sport Exhaust (PSE) | performance | $0 | ✅ Yes | $800 |
| `sport_seats.py` | Sport Seats | Sport Seats / Adaptive Sport Seats | seating | $0 | ✅ Yes | $500 |
| `heated_seats.py` | Heated Seats | Heated Seats | seating | $0 | ✅ Yes | $150 |
| `bose_surround_sound.py` | BOSE | BOSE Surround Sound | technology | $0 | ✅ Yes | $300 |
| `pcm_navigation.py` | PCM | PCM w/ Navigation | technology | $0 | ✅ Yes | $300 |
| `bi_xenon_headlights.py` | Bi-Xenon | Bi-Xenon Headlights with Dynamic Cornering | exterior | $0 | ✅ Yes | $250 |
| `upgraded_wheels.py` | Wheels | 18–19" Upgraded Wheels | exterior | $0 | ✅ Yes | $400 |
| `park_assist.py` | Park Assist | Park Assist | convenience | $0 | ✅ Yes | $200 |

**Total Value of Detected Options: $5,900**

## 📝 **Individual Option File Structure**

Each option file follows this exact template:

### **File: `sport_chrono.py`**
```python
"""
Sport Chrono Package Plus Option

This file contains everything needed to detect the Sport Chrono Package Plus option.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List


class SportChronoOption:
    """Sport Chrono Package Plus option detection and definition"""
    
    def __init__(self):
        # Option metadata
        self.id = "639/640"
        self.display = "Sport Chrono Package Plus"
        self.value_usd = 1000
        self.category = "performance"
        
        # Detection patterns - all variations that indicate this option
        self.patterns = [
            r"\bsport\s+chrono\b",
            r"\bchrono\s+package\b", 
            r"\bchrono\s+plus\b",
            # ... more patterns
        ]
        
        # Compile patterns for efficient matching
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for efficient matching"""
        # ... implementation
    
    def is_present(self, text: str, trim: str = None) -> bool:
        """Check if option is present in the given text"""
        # ... implementation
    
    def get_value(self, text: str, trim: str = None) -> int:
        """Get the value of the option if present"""
        # ... implementation
    
    def get_display(self) -> str:
        """Get the display name for this option"""
        # ... implementation
    
    def get_category(self) -> str:
        """Get the category for this option"""
        # ... implementation
    
    def get_id(self) -> str:
        """Get the ID for this option"""
        # ... implementation


# Export the option instance
SPORT_CHRONO_OPTION = SportChronoOption()
```

## 🧪 **Individual Option Testing**

### **Testing Sport Chrono Option File:**
```python
from x987.options.sport_chrono import SPORT_CHRONO_OPTION

# Test the option directly
print(f"ID: {SPORT_CHRONO_OPTION.get_id()}")                    # Output: 639/640
print(f"Display: {SPORT_CHRONO_OPTION.get_display()}")          # Output: Sport Chrono Package Plus
print(f"Category: {SPORT_CHRONO_OPTION.get_category()}")        # Output: performance
print(f"Base Value: ${SPORT_CHRONO_OPTION.get_value('test')}")  # Output: $0

# Test detection
text1 = "Sport Chrono Package Plus"
is_present1 = SPORT_CHRONO_OPTION.is_present(text1)             # Output: True
value1 = SPORT_CHRONO_OPTION.get_value(text1)                   # Output: $1000

text2 = "Chrono Package"
is_present2 = SPORT_CHRONO_OPTION.is_present(text2)             # Output: True
value2 = SPORT_CHRONO_OPTION.get_value(text2)                   # Output: $1000

text3 = "Just some text"
is_present3 = SPORT_CHRONO_OPTION.is_present(text3)             # Output: False
value3 = SPORT_CHRONO_OPTION.get_value(text3)                   # Output: $0
```

## 🔍 **Pattern Detection Examples**

### **Sport Chrono Patterns:**
1. `\bsport\s+chrono\b` - matches "Sport Chrono"
2. `\bchrono\s+package\b` - matches "Chrono Package"
3. `\bchrono\s+plus\b` - matches "Chrono Plus"
4. `\bsport\s+chrono\s+plus\b` - matches "Sport Chrono Plus"
5. `\bchrono\s+package\s+plus\b` - matches "Chrono Package Plus"
6. `\bsport\s+chrono\s+package\b` - matches "Sport Chrono Package"
7. `\bchrono\b` - matches "Chrono"
8. `\bsport\s+chrono\s+package\s+plus\b` - matches "Sport Chrono Package Plus"

### **BOSE Surround Sound Patterns:**
1. `\bbose\b` - matches "BOSE"
2. `\bbose\s+surround\s+sound\b` - matches "BOSE Surround Sound"
3. `\bsurround\s+sound\b` - matches "Surround Sound"
4. `\bpremium\s+sound\s+system\b` - matches "Premium Sound System"
5. `\bpremium\s+audio\b` - matches "Premium Audio"
6. `\bpremium\s+sound\b` - matches "Premium Sound"
7. `\bpremium\s+audio\s+system\b` - matches "Premium Audio System"
8. `\bupgraded\s+sound\s+system\b` - matches "Upgraded Sound System"

## 📈 **Output Consistency**

Every option file provides the same interface:

- **`get_id()`** - Returns the option identifier
- **`get_display()`** - Returns the human-readable name
- **`get_category()`** - Returns the option category
- **`get_value(text, trim)`** - Returns $0 if not present, option value if present
- **`is_present(text, trim)`** - Returns True/False based on detection

## 🎯 **Key Benefits Demonstrated**

### **1. See All Options at a Glance**
Just look at the file list - each file = one option:
- `sport_chrono.py` → Sport Chrono Package Plus
- `pasm.py` → PASM
- `bose_surround_sound.py` → BOSE Surround Sound
- etc.

### **2. Fix One Option - Edit Only That File**
- Problem with Sport Chrono detection? Edit `sport_chrono.py` only
- Need to improve BOSE patterns? Edit `bose_surround_sound.py` only
- Zero risk of breaking other options

### **3. Add New Options - Create New File**
1. Create `x987/options/new_option.py`
2. Follow the template
3. Export `NEW_OPTION_OPTION` instance
4. Done! Registry automatically discovers it

### **4. Complete Isolation**
Each option file is completely self-contained:
- Own patterns
- Own metadata
- Own detection logic
- No shared state or dependencies

## 🚀 **Real-World Usage**

### **In CSV Pipeline:**
```python
from x987.options.registry import OPTIONS_REGISTRY

# Get all options
all_options = OPTIONS_REGISTRY.get_all_options()

# Check each option in raw text
for option in all_options:
    if option.is_present(raw_text, trim):
        detected_options.append({
            'id': option.get_id(),
            'display': option.get_display(),
            'category': option.get_category(),
            'value': option.get_value(raw_text, trim)
        })
```

### **In Reports:**
```python
# Group by category
by_category = {}
for option in detected_options:
    category = option['category']
    if category not in by_category:
        by_category[category] = []
    by_category[category].append(option['display'])
```

## 🎉 **Summary**

The new one-option-per-file architecture provides:

- **11 individual option files** - each completely self-contained
- **Consistent output interface** - every option works the same way
- **Automatic discovery** - registry finds all options automatically
- **Zero dependencies** - modify one option without affecting others
- **Crystal clear organization** - file list shows exactly what's available
- **Easy maintenance** - fix issues in isolation
- **Simple extensibility** - add new options with new files

Each option file is a self-contained unit that can be developed, tested, and modified independently while providing consistent, reliable output when its option is detected.
