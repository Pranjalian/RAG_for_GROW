---
name: Groww Market Intelligence
colors:
  surface: '#0e1322'
  surface-dim: '#0e1322'
  surface-bright: '#343949'
  surface-container-lowest: '#090d1d'
  surface-container-low: '#161b2b'
  surface-container: '#1a1f2f'
  surface-container-high: '#25293a'
  surface-container-highest: '#303445'
  on-surface: '#dee1f7'
  on-surface-variant: '#bacac1'
  inverse-surface: '#dee1f7'
  inverse-on-surface: '#2b3040'
  outline: '#85948c'
  outline-variant: '#3c4a43'
  surface-tint: '#2fe0aa'
  primary: '#44edb7'
  on-primary: '#003828'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#006c4f'
  secondary: '#c3c6d8'
  on-secondary: '#2c303e'
  secondary-container: '#454958'
  on-secondary-container: '#b4b7ca'
  tertiary: '#ffc8a3'
  on-tertiary: '#502500'
  tertiary-container: '#ffa15b'
  on-tertiary-container: '#733800'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#dfe1f5'
  secondary-fixed-dim: '#c3c6d8'
  on-secondary-fixed: '#171b29'
  on-secondary-fixed-variant: '#424655'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb785'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#713700'
  background: '#0e1322'
  on-background: '#dee1f7'
  surface-variant: '#303445'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  container-max: 1440px
  gutter: 20px
---

## Brand & Style
The design system for this product is built on a foundation of "Precision Modernism." It is designed for high-stakes financial decision-making, where clarity, speed, and trust are paramount. The aesthetic targets professional investors and data-conscious users who require a high-density information environment that remains breathable and premium.

The visual direction combines **Minimalism** with subtle **Glassmorphism**. It utilizes a deep, monochromatic dark base to reduce eye strain during long sessions, punctuated by vibrant functional accents that guide the user's attention to critical market movements. The interface should feel like a high-end physical trading terminal: structured, responsive, and tactile.

## Colors
The palette is dominated by a deep obsidian core, ensuring that the primary "Groww Green" (#00d09c) acts as a beacon for action and growth. 

- **Primary & Accent:** Use the primary green exclusively for calls to action, growth indicators, and active states. 
- **Functional Palette:** Semantic colors (Success, Warning, Danger) are tuned for high legibility against dark backgrounds. Success and Danger colors should be used for price fluctuations (ticks) and status indicators.
- **Surface Hierarchy:** The background shifts from the deepest black (#0f1117) to a lighter surface (#242836) to indicate elevation. Borders should use a low-contrast version of the secondary text color at 15% opacity to maintain a clean, glass-like appearance without heavy visual weight.

## Typography
This design system utilizes **Inter** for all primary UI elements to ensure maximum readability and a neutral, professional tone. To lean into the "Market Intelligence" aspect, **JetBrains Mono** (or a similar high-quality monospaced font) is introduced specifically for numerical data, stock tickers, and tabular values to ensure vertical alignment and a technical feel.

- **Weight Usage:** Reserve Bold (700) for large display headers. Use Medium (500) for buttons and navigation items.
- **Data Display:** All price movements and percentage changes must use the `label-mono` style to ensure digits do not "jump" during live updates.
- **Contrast:** Always use `text_primary` for headlines and `text_secondary` for metadata and supporting descriptions.

## Layout & Spacing
The layout follows a **Fixed Grid** model for desktop dashboards to ensure data density is optimized and predictable. 

- **Grid System:** A 12-column grid with 20px gutters. On desktop, the main content area is capped at 1440px.
- **Spacing Rhythm:** Based on a 4px baseline. Use 16px (md) for standard padding within cards and 24px (lg) for section margins.
- **Adaptive Rules:** 
    - **Desktop:** Multi-pane layout with a fixed sidebar (240px).
    - **Tablet:** Sidebar collapses into a bottom navigation bar or hamburger menu; cards stack into 2 columns.
    - **Mobile:** Single column flow with 16px side margins. Data tables should allow horizontal scrolling or switch to a "list-card" view.

## Elevation & Depth
Elevation is expressed through **Tonal Layers** and **Glassmorphism** rather than traditional heavy shadows.

1.  **Level 0 (Background):** #0f1117 - The foundational canvas.
2.  **Level 1 (Cards/Panels):** #1a1d28 - Used for secondary grouping.
3.  **Level 2 (Active/Floating):** #242836 - Used for primary cards and interaction areas.
4.  **Glass Effect:** For modals and dropdowns, use the Level 2 color with 80% opacity and a 12px backdrop-blur filter.

**Outlines:** Instead of shadows, use a 1px solid border of `#ffffff` at 5% or 10% opacity on all Level 1 and Level 2 containers to define edges against the dark background.

## Shapes
The design system uses a **Soft** shape language to balance the technical, sharp nature of financial data with a modern, approachable feel.

- **Standard Radius:** 4px (0.25rem) for small components like checkboxes, tags, and input fields.
- **Component Radius:** 8px (0.5rem) for primary buttons and content cards.
- **Large Radius:** 12px (0.75rem) for major dashboard widgets and modals.

Avoid fully rounded "pill" shapes for buttons to maintain a more professional, institutional appearance.

## Components
- **Buttons:** Primary buttons use a solid `#00d09c` fill with black text for maximum contrast. Secondary buttons use a ghost style with a 1px border of the Primary color.
- **Data Grids:** Use a zebra-stripe pattern with Level 1 and Level 2 surfaces. Headers should be sticky with a slight glassmorphism blur. Row hover states should use a subtle highlight of 5% white overlay.
- **Chips/Status:** For "Up/Down" market indicators, use a "soft-pill" with 10% opacity fill of the semantic color (Success/Danger) and 100% opacity text.
- **Input Fields:** Dark fill (#1a1d28) with a 1px border. On focus, the border transitions to the Primary Green with a subtle outer glow (0px 0px 0px 2px rgba(0, 208, 156, 0.2)).
- **Cards:** All cards must feature the subtle 1px border. For "Market Open" or "Live" indicators, add a pulsating 6px dot using the Success color.
- **Charts:** Use thin 1.5pt lines for Sparklines. Areas under the line should feature a gradient fade from 20% opacity of the line color to 0%.