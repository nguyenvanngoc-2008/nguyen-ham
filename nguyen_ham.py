

import pygame
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import sympy
import re

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bộ Tính Nguyên Hàm")

TRANG = (255, 255, 255)
DEN = (0, 0, 0)
XAM = (200, 200, 200)
XAM_DEN = (80, 80, 80)
XANH = (100, 150, 255)
GREEN = (100, 200, 100)

FONT = pygame.font.SysFont("arial", 35)
FONT1 = pygame.font.SysFont("arial", 40)

bieuthuc_str = ""
hinh_kq = None
hinh_bt = None

def matpl(latex_str, font_size=22):
    if not latex_str.strip():
        return None
    try:
        fig, ax = plt.subplots(figsize=(4.5, 1), dpi=100)
        mpl_trang = (TRANG[0]/255, TRANG[1]/255, TRANG[2]/255)
        fig.patch.set_facecolor(mpl_trang)
        ax.text(0.5, 0.5, f"${latex_str}$", fontsize=font_size, ha='center', va='center', color=DEN)
        ax.axis('off')
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, facecolor=fig.get_facecolor())
        buf.seek(0)
        img_sur = pygame.image.load(buf, 'png')
        plt.close(fig)
        return img_sur
    except Exception:
        return None

def convert1(expr):
    expr = expr.strip()
    if not expr:
        return ""

    if expr.startswith('(') and expr.endswith(')'):
        plv = 0
        is_wrapped = True
        for i, char in enumerate(expr[1:-1]):
            if char == '(': plv += 1
            elif char == ')': plv -= 1
            if plv < 0:
                is_wrapped = False
                break
        if is_wrapped and plv == 0:
            nd_trong = convert1(expr[1:-1])
            return r"\left( " + nd_trong + r" \right)"

    plv = 0
    for i in range(len(expr) - 1, -1, -1):
        char = expr[i]
        if char == ')': plv += 1
        elif char == '(': plv -= 1
        elif plv == 0 and char in ['+', '-']:
            if i > 0 and expr[i-1].lower() not in "+-*/^(e":
                return f"{{{convert1(expr[:i])}}} {char} {{{convert1(expr[i+1:])}}}"

    plv = 0
    for i in range(len(expr) - 1, -1, -1):
        char = expr[i]
        if char == ')': plv += 1
        elif char == '(': plv -= 1
        elif plv == 0:
            if char == '*':
                return f"{{{convert1(expr[:i])}}} " + r" \cdot " + f"{{{convert1(expr[i+1:])}}}"
            if char == '/':
                return r"\frac{" + convert1(expr[:i]) + r"}{" + convert1(expr[i+1:]) + r"}"

    plv = 0
    for i in range(len(expr)):
        char = expr[i]
        if char == '(': plv += 1
        elif char == ')': plv -= 1
        elif plv == 0 and char == '^':
            return f"{{{convert1(expr[:i])}}}^{{{convert1(expr[i+1:])}}}"
    expr = expr.replace('pi', r'\pi ')
    expr = expr.replace('log(', r'\log_{10}(')
    expr = expr.replace('ln(', r'\ln(')
    return expr
def nguyen_ham(expr_str):
    if not expr_str:
        return ""
    try:
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
        x = sympy.Symbol('x')
        
        bt_string1 = expr_str.replace('^', '**')
        bt_string1 = bt_string1.replace('log(', 'log10(')
        bt_string1 = bt_string1.replace('ln(', 'log(')
        bt_string1 = bt_string1.replace('cot(', 'cot(')
        bt_string1 = bt_string1.replace('pi', 'pi')
        bt_string1 = bt_string1.replace('e', 'E')

        rut_gon = (standard_transformations + (implicit_multiplication_application,))
        sy = {
            "E": sympy.E, "pi": sympy.pi,
            "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan, "cot": sympy.cot,
            "Integer": sympy.Integer, "Float": sympy.Float, "Rational": sympy.Rational, "Symbol": sympy.Symbol
        }
        parsed_expr = parse_expr(bt_string1,
                                 local_dict={'x': x},
                                 global_dict=sy,
                                 transformations=rut_gon)

        tp_bt = sympy.integrate(parsed_expr, x)
        rut_gon1 = sympy.simplify(tp_bt)
        latex_result = sympy.latex(rut_gon1)
        #latex_result = re.sub(r'\\log{\\left\\((.*?)\\right\\)}', r'\\ln{\\left|\1 \\right|}', latex_result)
        s=""
        tt=False
        print(latex_result)
        #print(len(latex_result))
        print(latex_result)
        for i in range(len(latex_result)):
            if latex_result[i]=='l' and latex_result[i+1]=='o' and latex_result[i+2]=='g' and i+3<len(latex_result):
                s+='ln'
                tt=i+2
            if i>tt or tt==False:
                s+=latex_result[i]
        if tt!=False:
            for i in s:
                if i=='('or i==')':
                    s=s.replace(i,'|')
        print(s)
        s += " + C"
        return s

    except Exception as e:
        print(e)
        return "Lỗi cú pháp"

class Button:
    def __init__(self, x, y, w, h, label, value=None, color=XAM_DEN):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.value = value if value is not None else label
        self.color = color
        self.text_color = TRANG

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        text_surf = FONT.render(self.label, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
buttons = []
btn_w, btn_h, gap = 80, 50, 10
x_coords = [10, 100, 190, 280, 370]
y_coords = [150, 210, 270, 330, 390, 450]
rows = [
    [('sin', 'sin('), ('cos', 'cos('), ('tan', 'tan('), ('cot', 'cot('), ('e', 'e')],
    [('xʸ', '^'), ('(', '('), (')', ')'), ('C', 'clear'), ('DEL', 'backspace')],
    [('7', '7'), ('8', '8'), ('9', '9'), ('÷', '/'), ('×', '*')],
    [('4', '4'), ('5', '5'), ('6', '6'), ('+', '+'), ('-', '-')],
    [('1', '1'), ('2', '2'), ('3', '3'), ('log', 'log('), ('ln', 'ln(')],
    [('0', '0'), ('.', '.'), ('x', 'x'), ('π', 'pi'), ('∫dx', 'integrate')]
]

for r_idx, row_content in enumerate(rows):
    for c_idx, (label, value) in enumerate(row_content):
        color = XAM_DEN
        if value == 'integrate':
            color = GREEN
        elif value in ['clear', 'backspace']:
            color = (200, 100, 100)

        buttons.append(Button(x_coords[c_idx], y_coords[r_idx], btn_w, btn_h, label, value, color))
running = True
needs_render = True
display_rect = pygame.Rect(10, 20, 480, 120)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.is_clicked(event.pos):
                    action = button.value
                    if action == "clear":
                        bieuthuc_str = ""
                        hinh_kq = None
                    elif action == "backspace":
                        if bieuthuc_str:
                            bieuthuc_str = bieuthuc_str[:-1]
                        hinh_kq = None
                    elif action == "integrate":
                        latex_result = nguyen_ham(bieuthuc_str)
                        font_size = 22 
                        hinh_kq = matpl(latex_result, font_size=font_size)
                        if hinh_kq and hinh_kq.get_width() > display_rect.width - 30:
                            while font_size > 10 and hinh_kq and hinh_kq.get_width() > display_rect.width - 30:
                                font_size -= 2 
                                hinh_kq = matpl(latex_result, font_size=font_size)
                    else:
                        bieuthuc_str += action
                    needs_render = True
    if needs_render:
        latex_expr_display = convert1(bieuthuc_str)
        hinh_bt = matpl(latex_expr_display)
        if hinh_bt is None and bieuthuc_str:
            hinh_bt = FONT1.render(bieuthuc_str, True, DEN)
        needs_render = False
    screen.fill(XAM)
    display_rect = pygame.Rect(10, 20, 480, 120)
    pygame.draw.rect(screen, TRANG, display_rect, border_radius=10)
    pygame.draw.rect(screen, XANH, display_rect, 3, border_radius=10)
    if hinh_bt:
        img_rect = hinh_bt.get_rect(centery=display_rect.centery - 9)
        if img_rect.width > display_rect.width - 20:
            img_rect.right = display_rect.right - 10
        else:
            img_rect.centerx = display_rect.centerx
        screen.blit(hinh_bt, img_rect)
    if hinh_kq:
        res_rect = hinh_kq.get_rect(right=display_rect.right - 15, bottom=display_rect.bottom - 10)
        screen.blit(hinh_kq, res_rect)
    for button in buttons:
        button.draw(screen)
    pygame.display.flip()
pygame.quit()
