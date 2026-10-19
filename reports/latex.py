"""
Text and numbers into LaTeX: escaping, the dashboard's unicode symbols as math, numbers through siunitx.
"""
import math
import re

_SPECIAL = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}

# Unicode used in dashboard labels and units -> math
_UNICODE = {
    "₀": "$_0$", "₁": "$_1$", "₂": "$_2$", "₃": "$_3$", "₄": "$_4$", "₅": "$_5$", "₆": "$_6$",
    "²": "$^2$", "³": "$^3$", "·": r"$\cdot$", "−": "$-$", "°": r"$^\circ$",
    "ψ": r"$\psi$", "ρ": r"$\rho$", "η": r"$\eta$", "π": r"$\pi$", "φ": r"$\phi$", "ṁ": r"$\dot{m}$"}

# FlowState field -> symbol
FIELD_SYMBOLS = {
    "Tt": r"$T_t$", "Pt": r"$P_t$", "T": r"$T$", "P": r"$P$", "M": r"$M$", "V": r"$V$",
    "rho": r"$\rho$", "rho_t": r"$\rho_t$", "m_dot": r"$\dot{m}$"}


def escape(text: str) -> str:
    """Plain text -> LaTeX: specials escaped, known unicode symbols set as math."""
    out = "".join(_SPECIAL.get(c, c) for c in str(text))
    out = re.sub("([A-Za-z])([₀-₉])", lambda m: f"${m[1]}_{ord(m[2]) - ord('₀')}$", out)   # M₀ -> $M_0$
    for k, v in _UNICODE.items():
        out = out.replace(k, v)
    return re.sub(r"(?<!\\)\$\$", "", out)      # adjacent symbols merge into one math run


PROPER_NOUNS = {"Mach", "Reynolds", "Prandtl", "Nusselt", "TSFC"}


def in_sentence(name: str) -> str:
    """'Turbine entry temperature' -> 'turbine entry temperature'; 'Mach number M₀' stays."""
    return name if name.split(" ")[0] in PROPER_NOUNS else name[:1].lower() + name[1:]


def split_unit(label: str) -> tuple[str, str]:
    """'Tip speed [m/s]' -> ('Tip speed', 'm/s')."""
    m = re.fullmatch(r"(.*?)\s*\[(.*)\]", label)
    return (m[1], m[2]) if m else (label, "")


def num(value, sig: int = 4) -> str:
    """A number for a table: siunitx, `sig` significant figures; missing / non-finite -> en dash."""
    if value is None or not math.isfinite(value):
        return "--"
    if value == 0:
        return r"\num{0}"
    mag = math.floor(math.log10(abs(value)))
    if not -3 <= mag < 6:
        return rf"\num{{{value:.{sig}g}}}"
    decimals = max(sig - 1 - mag, 0)
    text = f"{round(value, decimals):.{decimals}f}"
    return rf"\num{{{text.rstrip('0').rstrip('.') if '.' in text else text}}}"


def coord(value: float) -> str:
    """A plot coordinate, compact."""
    return f"{value:.6g}"
