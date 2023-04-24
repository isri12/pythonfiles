from turtle import *
import turtle

# color('red', 'yellow')
# begin_fill()
# while True:
#     forward(200)
#     left(200)
#     if abs(pos()) < 1:
#         break
# end_fill()
# done()


# Create a turtle object
pen = turtle.Turtle()

# Move the turtle to the starting position
pen.penup()
pen.goto(-100, 100)
pen.pendown()

# Draw a square
for i in range(100):
    pen.forward(200)
    pen.right(200)

    pen.forward(100)
    pen.right(100)

# Exit the program when the user clicks the window
turtle.exitonclick()