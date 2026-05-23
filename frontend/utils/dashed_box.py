import flet as ft
import math 
import flet.canvas as cv

def dashed_box(width, height, content, border_color, border_thickness=1.5, dash_len=10, gap_len=8, bgcolor=None, border_radius=16):
    elements = []
    
    def add_dashed_line(x1, y1, x2, y2):
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0: return
        dx, dy = (x2 - x1) / length, (y2 - y1) / length
        curr = 0
        drawing = True
        elements.append(cv.Path.MoveTo(x1, y1))
        
        while curr < length:
            step = min(dash_len if drawing else gap_len, length - curr)
            next_x = x1 + dx * (curr + step)
            next_y = y1 + dy * (curr + step)
            if drawing:
                elements.append(cv.Path.LineTo(next_x, next_y))
            else:
                elements.append(cv.Path.MoveTo(next_x, next_y))
            curr += step
            drawing = not drawing

    inset = border_thickness / 2
    right = width - inset
    bottom = height - inset
    
    add_dashed_line(inset, inset, right, inset)      
    add_dashed_line(right, inset, right, bottom)     
    add_dashed_line(right, bottom, inset, bottom)    
    add_dashed_line(inset, bottom, inset, inset)     

    dashed_canvas = cv.Canvas(
        [
            cv.Path(
                elements=elements,
                paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=border_thickness, color=border_color)
            )
        ],
        width=width, height=height,
    )

    return ft.Stack(
        [
            ft.Container(
                width=width, height=height,
                bgcolor=bgcolor,
                border_radius=border_radius,
                content=dashed_canvas,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS, 
            ),
            ft.Container(
                width=width, height=height,
                content=content,
                alignment=ft.Alignment.CENTER,
            )
        ],
        width=width, height=height,
    )