# Color System Reference

This document provides a comprehensive reference for all colors used in the QAI application. All colors are defined as CSS variables in `src/app/globals.css` and can be used with Tailwind classes.

## Gray Scale

- `--gray-light`: #f9f9f9 (Lightest gray)
- `--gray-medium`: #808080 (Medium gray)
- `--gray-dark`: #676767 (Dark gray)
- `--gray-darker`: #525252 (Darker gray)
- `--gray-darkest`: #A9A9A9 (Darkest gray)

## Usage Examples

### Tailwind Classes

```css
/* Background colors */
bg-gray-light
bg-gray-medium
bg-gray-dark
bg-gray-darker
bg-gray-darkest

/* Text colors */
text-gray-light
text-gray-medium
text-gray-dark
text-gray-darker
text-gray-darkest

/* Border colors */
border-gray-light
border-gray-medium
border-gray-dark
border-gray-darker
border-gray-darkest

/* Hover states */
hover:bg-gray-light
hover:text-gray-darkest
```

### CSS Variables

```css
.custom-element {
  background-color: var(--gray-darkest);
  color: var(--gray-light);
  border: 1px solid var(--gray-dark);
}
```
