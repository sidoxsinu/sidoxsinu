# Scaling factor
scale = .5

# Center flower with layered circles
center_core = circle(r=15*scale, fill='deeppink') + \
              circle(r=35*scale, fill='gold') + \
              circle(r=55*scale, fill='orange') + \
              circle(r=75*scale, fill='red')+ \
               circle(r=50*scale, fill='blue')+ \
                circle(r=25*scale, fill='brown')

# Rotating square petals (5 layers)
petal1 = rectangle(w=85*scale, h=85*scale, fill='salmon') | repeat(30, rotate(12))
petal2 = rectangle(w=90*scale, h=90*scale, fill='yellow') | repeat(30, rotate(12))
petal3 = rectangle(w=100*scale, h=100*scale, fill='violet') | repeat(30, rotate(12))
petal4 = rectangle(w=110*scale, h=110*scale, fill='yellow') | repeat(30, rotate(12))
petal5 = rectangle(w=120*scale, h=120*scale, fill='magenta') | repeat(30, rotate(12))
petals = petal1 + petal2 + petal3 + petal4 + petal5

# White and green base circles
white_base = circle(r=170*scale, fill='yellow')
green_base = circle(r=180*scale, fill='yellowgreen')

# Floral radial rings (ellipses as petals)
ring1 = ellipse(w=30*scale, h=150*scale, fill='yellow') | translate(y=150*scale) | repeat(12, rotate(30))
ring2 = ellipse(w=30*scale, h=145*scale, fill='orange') | translate(y=145*scale) | repeat(12, rotate(30))
ring3 = ellipse(w=30*scale, h=140*scale, fill='gold') | translate(y=140*scale) | repeat(12, rotate(30))
ring4 = ellipse(w=30*scale, h=135*scale, fill='deeppink') | translate(y=135*scale) | repeat(12, rotate(30))
ring5 = ellipse(w=30*scale, h=130*scale, fill='yellow') | translate(y=130*scale) | repeat(12, rotate(30))
ring6 = ellipse(w=30*scale, h=125*scale, fill='hotpink') | translate(y=125*scale) | repeat(12, rotate(30))
ring7 = ellipse(w=30*scale, h=120*scale, fill='yellow') | translate(y=120*scale) | repeat(12, rotate(30))

# Leafy green base
leaf_base = ellipse(w=480*scale, h=100*scale, fill='darkgreen') | translate(y=240*scale) | repeat(8, rotate(45))

# Radiating outer petals
outer1 = ellipse(w=240*scale, h=60*scale, fill='yellow') | translate(y=240*scale) | repeat(8, rotate(45))
outer2 = ellipse(w=220*scale, h=60*scale, fill='orange') | translate(y=220*scale) | repeat(8, rotate(45))
outer3 = ellipse(w=200*scale, h=60*scale, fill='hotpink') | translate(y=200*scale) | repeat(8, rotate(45))

# Decorative outer circles
outer_dots = circle(r=50*scale, fill='lightpink') | translate(y=100*scale) | repeat(5, rotate(72))

# Combine all layers (background first, center last)
result = leaf_base + \
         outer1 + outer2 + outer3 + \
         ring1 + ring2 + ring3 + ring4 + ring5 + ring6 + ring7 + \
         green_base + white_base + petals + \
         outer_dots + center_core


# I prompted to design this Pookalam by choosing the colors, shapes, sizes,
# and layering to create a vibrant, symmetrical pattern inspired by traditional motifs
# created this Pookalam with the use of circles, rectangles, and ellipses 
# build layers of petals and shapes that form a balanced, symmetrical pattern.
# I chose warm colors like orange, yellow, and pink to give the design energy and
# warmth. My goal was to make something colorful and lively that reflects happiness
# and togetherness during celebrations. I used ChatGPT to help me write and organize
# the code following the design rules, which made the process easier and more fun.