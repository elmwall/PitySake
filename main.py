import event_calculator

# try:
#     event = int(input("Enter event occurrence: "))
# except:
#     event = 0
# if event not in range (1,91):
#     if type(event) is int:
#         print("Invalid number.")
#     print("Enter page and row of previous and current event.")
#     event = event_calculator.main()

# print(f"Event occurred at attempt {event}.")
    
event = event_calculator.main()
print(event)
