/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F5F5F0",
        surface: "#EFEFEA",
        primary: "#1A1A1A",
        accent: "#E8E8E0",
        "text-primary": "#1A1A1A",
        "text-secondary": "#555550",
      },
      fontFamily: {
        sans: ['"Space Grotesk"', '"Inter"', "system-ui", "sans-serif"],
        mono: ['"Space Mono"', '"JetBrains Mono"', "monospace"],
      },
      boxShadow: {
        brutal: "4px 4px 0px #000000",
        "brutal-sm": "2px 2px 0px #000000",
        "brutal-lg": "6px 6px 0px #000000",
        "brutal-hover": "2px 2px 0px #000000",
      },
    },
  },
  plugins: [],
};
