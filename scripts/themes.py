"""Famous editor palettes, one per README section, so every block of a section shares one coherent theme.

    from themes import TOKYO_NIGHT as T      # T["bg"], T["accent"], ...

Keys: bg (window body), surface (a shade darker: banners, header), border, fg (text), dim (comments, prompts),
accent (main color of the section), and a few named hues used for small highlights.
"""

TOKYO_NIGHT = dict(      # projects, project cards, the "more" button
    name="Tokyo Night", bg="#1a1b26", surface="#16161e", border="#3b4261", fg="#c0caf5", dim="#565f89", soft="#a9b1d6",
    accent="#7aa2f7", violet="#bb9af7", green="#9ece6a", yellow="#e0af68", red="#f7768e", cyan="#7dcfff")

NORD = dict(             # research
    name="Nord", bg="#2e3440", surface="#272c36", border="#4c566a", fg="#eceff4", dim="#616e88", soft="#d8dee9",
    accent="#a3be8c", violet="#b48ead", green="#a3be8c", yellow="#ebcb8b", red="#bf616a", cyan="#88c0d0")

CATPPUCCIN = dict(       # roles (Mocha)
    name="Catppuccin Mocha", bg="#1e1e2e", surface="#181825", border="#45475a", fg="#cdd6f4", dim="#6c7086", soft="#9399b2",
    accent="#cba6f7", violet="#cba6f7", green="#a6e3a1", yellow="#f9e2af", red="#f38ba8", cyan="#89dceb")

DRACULA = dict(          # stack and contribution calendars
    name="Dracula", bg="#282a36", surface="#21222c", border="#44475a", fg="#f8f8f2", dim="#6272a4", soft="#bfbfbf",
    accent="#ff79c6", violet="#bd93f9", green="#50fa7b", yellow="#f1fa8c", red="#ff5555", cyan="#8be9fd")

ROSE_PINE = dict(        # achievements
    name="Rosé Pine", bg="#191724", surface="#1f1d2e", border="#403d52", fg="#e0def4", dim="#6e6a86", soft="#908caa",
    accent="#f6c177", violet="#c4a7e7", green="#9ccfd8", yellow="#f6c177", red="#eb6f92", cyan="#9ccfd8")

SOLARIZED = dict(        # the pac-man contributions graph
    name="Solarized Dark", bg="#002b36", surface="#00212b", border="#0f4a58", fg="#93a1a1", dim="#586e75", soft="#839496",
    accent="#b58900", violet="#6c71c4", green="#859900", yellow="#b58900", red="#dc322f", cyan="#2aa198")

GRUVBOX = dict(          # the header
    name="Gruvbox Dark", bg="#1d2021", surface="#1d2021", border="#504945", fg="#ebdbb2", dim="#928374", soft="#a89984",
    accent="#fabd2f", violet="#d3869b", green="#b8bb26", yellow="#fabd2f", red="#fb4934", cyan="#8ec07c")
