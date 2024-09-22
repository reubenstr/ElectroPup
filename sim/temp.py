  

shoulder_length = 0.010
upper_leg_length = 0.140
lower_leg_length = 0.140

x= 0 
y= 0
z = 0


top = (y**2 + (-z)**2 - shoulder_length**2 + (-x)**2 - upper_leg_length**2 - lower_leg_length**2) 
bottom = (2 * lower_leg_length * upper_leg_length)

domain = top / bottom

print (domain)




