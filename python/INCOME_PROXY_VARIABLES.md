# Income Proxy Variables in SCoRE Data

## Overview

The SCoRE survey does **not** directly measure household or individual income. However, several variables can serve as proxies for socioeconomic status and income level.

---

## Primary Income Proxy: Asset Ownership (B14)

The **best available income proxy** is the asset ownership battery (B14), which measures wealth rather than income but is strongly correlated with income level.

| Variable | Question | Values | N (Yes) |
|----------|----------|--------|---------|
| `b14_1` | Owns home (eigen huis) | 0=No, 1=Yes | 4,855 (60.6%) |
| `b14_2` | Owns other real estate | 0=No, 1=Yes | 310 (3.9%) |
| `b14_3` | Has savings account | 0=No, 1=Yes | 5,486 (68.5%) |
| `b14_4` | Owns stocks/bonds | 0=No, 1=Yes | 1,007 (12.6%) |
| `b14_5` | None of these | 0=No, 1=Yes | 1,360 (17.0%) |

### Recommended Composite Index

Create a **wealth index** by summing asset ownership:

```python
# Wealth index (0-4 scale)
wealth_index = b14_1 + b14_2 + b14_3 + b14_4

# Alternative: Binary high/low wealth
high_wealth = (wealth_index >= 2)  # Owns home + savings or more
```

**Interpretation:**
- 0 = No assets (lowest SES)
- 1 = One type of asset
- 2 = Two types (typically home + savings)
- 3-4 = Multiple assets (highest SES)

---

## Secondary Proxy: Occupation Classification (B13)

The NS-SEC-style occupation classification provides a socioeconomic gradient:

| Code | Category | N | Typical Income Level |
|------|----------|---|---------------------|
| 3 | Senior management/administration | 749 | Highest |
| 8 | Traditional professional (accountant, doctor, engineer) | 808 | High |
| 1 | Modern professional (teacher, nurse, social worker) | 1,217 | Middle-High |
| 7 | Middle/junior management | 928 | Middle |
| 4 | Technical/craft occupations | 985 | Middle |
| 2 | Clerical/administrative | 1,475 | Middle-Low |
| 5 | Semi-routine manual/service | 891 | Low |
| 6 | Routine manual/service | 830 | Lowest |

### Recommended Recoding

```python
# Create occupational class variable (NS-SEC style)
occupation_class = {
    3: 'Higher managerial',    # Highest
    8: 'Higher professional',
    1: 'Lower professional',
    7: 'Lower managerial',
    4: 'Intermediate',
    2: 'Lower supervisory',
    5: 'Semi-routine',
    6: 'Routine'               # Lowest
}

# Binary: Professional/managerial vs. working class
professional_class = b13 in [1, 3, 7, 8]
```

---

## Additional Proxies

### Employment Situation (B07)

| Code | Status | Typical Income |
|------|--------|----------------|
| 1 | Employed | Varies by occupation |
| 2 | In education | Low (student) |
| 3 | Unemployed (seeking) | Very low |
| 4 | Unemployed (not seeking) | Very low |
| 5 | Disabled | Low (benefits) |
| 6 | Retired | Varies (pension) |
| 7 | Homemaker | Depends on household |
| 8 | Other | Unknown |

### Organization Type (B10)

| Code | Sector | Typical Income |
|------|--------|----------------|
| 1 | Central/local government | Middle-High |
| 2 | Public sector (education, health) | Middle |
| 3 | State-owned enterprise | Middle-High |
| 4 | Private firm | Varies |
| 5 | Self-employed | Varies (often higher) |
| 6 | Other | Unknown |

### Home Ownership (B14_1)

Single binary indicator strongly correlated with income:
- **Homeowner** = Generally higher income/wealth
- **Renter** = Generally lower income/wealth

In the Netherlands, ~60% of respondents own their home.

---

## Recommended Implementation

### 1. Create Wealth Index

```python
def create_wealth_index(df):
    """Create composite wealth index from asset ownership."""
    # Sum of assets owned (0-4 scale)
    df['wealth_index'] = (
        df['b14_1'].fillna(0) +  # Home
        df['b14_2'].fillna(0) +  # Other real estate
        df['b14_3'].fillna(0) +  # Savings
        df['b14_4'].fillna(0)    # Stocks/bonds
    )

    # Binary: High wealth (2+ assets) vs. low wealth
    df['high_wealth'] = (df['wealth_index'] >= 2).astype(int)

    # Tertiles
    df['wealth_tertile'] = pd.qcut(
        df['wealth_index'],
        q=3,
        labels=['Low', 'Medium', 'High'],
        duplicates='drop'
    )

    return df
```

### 2. Create Occupation Class

```python
def create_occupation_class(df):
    """Create socioeconomic class from occupation."""
    # Higher class = professional/managerial occupations
    higher_class = [1, 3, 7, 8]  # Modern prof, Senior mgmt, Middle mgmt, Trad prof
    df['professional_class'] = df['b13'].isin(higher_class).astype(int)

    # Detailed class categories
    class_map = {
        3: 1,  # Senior management → 1 (highest)
        8: 2,  # Traditional professional
        1: 3,  # Modern professional
        7: 4,  # Middle management
        4: 5,  # Technical
        2: 6,  # Clerical
        5: 7,  # Semi-routine
        6: 8   # Routine → 8 (lowest)
    }
    df['occupation_rank'] = df['b13'].map(class_map)

    return df
```

### 3. Test H3 (Income Moderation)

```python
# Add interaction term to model
model_formula = """
    DV_single ~ b_perc_low40_hh * wealth_index +
    age + C(sex) + education + C(employment_status) +
    C(occupation) + born_in_nl
"""

# Or use binary:
model_formula = """
    DV_single ~ b_perc_low40_hh * high_wealth + ...
"""
```

---

## Variables to Extract from SCoRE

Add these to `config.py`:

```python
# Additional variables for income proxy
ADDITIONAL_SURVEY_COLUMNS = {
    # Asset ownership (wealth proxy)
    "b14_1": "owns_home",
    "b14_2": "owns_other_property",
    "b14_3": "has_savings",
    "b14_4": "owns_stocks",
    "b14_5": "no_assets",

    # Occupation details
    "b13": "occupation_class",
    "b10": "organization_type",
    "b09": "employee_type",  # employee, self-employed, family business
    "b11": "has_supervisory_role",
    "b12_1": "n_supervised",
}
```

---

## Theoretical Justification

Using **wealth** (assets) rather than **income** as a proxy has some advantages:

1. **Wealth is more stable** than income (less year-to-year fluctuation)
2. **Wealth captures lifetime earnings** better than current income
3. **Home ownership** is a particularly strong predictor of socioeconomic position in the Netherlands
4. **Asset ownership** reflects both past earnings and future security

However, limitations include:
- Wealth ≠ Income (especially for elderly with assets but low pension)
- Home ownership varies by age and region
- Missing actual income makes H3 test approximate

---

## Summary

| Proxy | Variable(s) | Best For |
|-------|-------------|----------|
| **Wealth Index** | b14_1 + b14_2 + b14_3 + b14_4 | Overall SES, H3 moderation test |
| **Home Ownership** | b14_1 | Simple binary SES indicator |
| **Occupation Class** | b13 | Employment-based SES |
| **Professional Status** | b13 in [1,3,7,8] | Binary class indicator |

**Recommendation:** Use the **wealth index** as primary income proxy for testing H3, with **occupation class** as sensitivity check.
