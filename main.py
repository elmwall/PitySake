import event_calculator

try:
    event = int(input("Enter event occurrence: "))
except:
    event = 0

if event not in range (1,91):
    event = event_calculator.main()

print(f"Event occurred at attempt {event}.")
    
