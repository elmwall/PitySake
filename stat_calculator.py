import os, math, statistics
from utilities import Archivist, Negotiator
# from event_calculator import Mathematician
from config import PATHWAYS


def collect(library):
    event_term = data_options["Term"]["Event"]
    attempt_term = data_options["Term"]["Attempt"]
    name_w_events = dict()
    for name, data in library.items():
        print()
        print(name)
        # print(library[name][event_term])
        # print(event_term, data)
        if event_term in data:
            # print(data[event_term])
            events = data[event_term]
        else:
            continue
        # print(events)
        # name_w_events[name] = library[name][event_term][attempt_term]
        for event_id, event_data in events.items():
            print(event_data)
            # print(event_at_date)
            if event_data[attempt_term]:
                name_w_events[f"{name} {event_id}"] = event_data[attempt_term]
            # print(date, events[date][attempt_term])
    
    print(name_w_events.items())
    attempt_values = [x for x in name_w_events.values()]
    print(attempt_values)
    average_attempt = statistics.mean(name_w_events.values())
    print(int(average_attempt))





arciv = Archivist(PATHWAYS["Directory"])
negotiator = Negotiator()
filepath = PATHWAYS["Character"] 
library = arciv.reader(filepath, join=True)
# library = arciv.reader(file)
# print(file)
data_options = arciv.reader(PATHWAYS["Options"], join=True)
# print(data_options)
# collection = file["Character"]

# print(file)


collect(library)


