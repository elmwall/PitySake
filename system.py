

class Administrator:
    def __init__(self):
        pass

    def edit_options(self, negotiator, data_options, data_validation):
        """
        ...
        """

        selectable_options = str()
        for category, info in data_validation.items():
            selectable_options += f"{category:18}- {info["editable"]}\n"
        option_type = negotiator.listed_options(
            f"Select option type to edit among:\n{selectable_options}",
            list(data_validation.keys())
        )

        # Data with structure data_options[option_type][attribute][detail_list]
        if data_validation[option_type]["can_change"]["category"]:
            selectable_options = list(data_options[option_type].keys())
            for x in data_validation[option_type]["standard_categories"].keys():
                if not data_validation[option_type]["standard_categories"][x]: selectable_options.remove(x)
            selectable_options.extend(["Add attribute", "Remove attribute"])
            attribute = negotiator.listed_options(
                f"Select category to change, or add/remove category:",
                selectable_options
            )

            if attribute == "Add attribute":
                new_attribute = negotiator.request_word("Name new category", "Name")
                min_details = 2
                message = f"The category need at least {min_details} options"
                new_attribute_details, new_detail = self._expand_list(negotiator, message, min_additions=min_details)

                data_options[option_type][new_attribute] = new_attribute_details
            elif attribute == "Remove attribute":
                attributes = list(data_options[option_type].keys())
                for att in data_validation[option_type]["standard_categories"].keys():
                    if att in attributes: attributes.remove(att)
                if len(attributes) == 0:
                    print("No removable categories.")
                    quit()
                remove_attribute = negotiator.listed_options("Select attribute to remove", attributes)
                data_options[option_type].pop(remove_attribute)
            else:
                data_options[option_type][attribute], new_detail = self._list_manager(negotiator, data_options[option_type], data_validation[option_type], subcategory=attribute)
                resolved_dependece, resolved_data = self._resolve_dependence(negotiator, data_options, data_validation, option_type, data_options[option_type][attribute], selection=attribute)
                if resolved_dependece: data_options = resolved_data

        # Data with structure data_options[option_type][detail_list]
        elif data_validation[option_type]["can_change"]["list"]:
            data_options[option_type], new_detail = self._list_manager(negotiator, data_options[option_type], data_validation[option_type], add_multiple=False)
            resolved_dependece, resolved_data = self._resolve_dependence(negotiator, data_options, data_validation, option_type, new_detail)
            if resolved_dependece: data_options = resolved_data
  
        # Data with structure data_options[option_type][sub_category][detail]
        elif data_validation[option_type]["can_change"]["subcategory"]:
            selectable_options = list()
            # Arrange data as [option_type, sub_category, detail]
            for x, y in data_options[option_type].items():
                if type(y) is dict: 
                    for v, w in y.items():
                        selectable_options.append([x, v, w])
                else:
                    selectable_options.append([None, x, y])
            message = "Select value to change:\n\n"
            message += f"   {"#":<2}: {"Category":18}{"Source":14}{"Amount":^6}\n"
            counter = 1
            indx = list()
            for x in selectable_options:
                message += f"   {counter:<2}: {str(x[0]):18}{str(x[1]):14}{x[2]:^6}\n"
                indx.append(counter)
                counter += 1
            print(message)
            detail = selectable_options[negotiator.request_key(indx, needs_int=True) - 1]
            title = f"{detail[0]}, {detail[1]}" if detail[0] else f"{detail[1]}"
            new_value = negotiator.request_numeral(
                f"Enter new value for {title}",
                lower_limit = 50,
                upper_limit = 200
            )
            data_options[option_type][detail[0]][detail[1]] = new_value
        
        return data_options


    def _resolve_dependence(self, negotiator, data_options, data_validation, option_type, new_value, selection=False):
        is_altered = False
        if "dependence" not in data_validation[option_type].keys():
            return is_altered, None
        option_type_dep = data_validation[option_type]["dependence"]

        for target_cat in option_type_dep.keys():
            if selection:
                if not selection in option_type_dep[target_cat].keys(): continue
            if option_type_dep[target_cat]["method"] == "copy":
                translation = option_type_dep[target_cat][selection]
                data_options[target_cat][translation] = new_value
                is_altered = True
            elif option_type_dep[target_cat]["method"] == "set_subcats":
                if new_value[:7] == "remove_":
                    for x, y in data_options[target_cat].items():
                        if type(y) is int: continue
                        if new_value[7:] in y.keys(): 
                            y.pop(new_value[7:])
                            is_altered = True
                    continue
                option_type_dep[target_cat].pop("method")
                for x, y in option_type_dep[target_cat].items():
                    if y == "ask": y = negotiator.confirm_action(f"Do you wish to connect {x} to {new_value} category?", is_enforced=True)
                    if not y: continue
                    data_options[target_cat][x][new_value] = negotiator.request_numeral(
                        f"Set {target_cat} value for {x} in {new_value} category.",
                        lower_limit=50,
                        upper_limit=200
                    )
                    is_altered = True
        return is_altered, data_options


    def _list_manager(self, negotiator, category, validate, subcategory=False, add_multiple=True):
        selection = negotiator.listed_options("Select action", ["Add new detail", "Remove detail"])
        if selection == "Add new detail":
            message = "Add addional option"
            detail_list = category[subcategory].copy() if subcategory else category
            output_list, new_detail = self._expand_list(negotiator, message, details=detail_list, ask_for_more=add_multiple)
            return output_list, new_detail
        else:
            details = category[subcategory].copy() if subcategory else category.copy()
            valid_info = validate["standard_categories"][subcategory] if subcategory else validate["standard_categories"]
            for det in valid_info:
                if det in details: details.remove(det)
            if len(details) == 0:
                print("No removable details.")
                quit()
            remove_detail = negotiator.listed_options("Select detail to remove", details)
            if subcategory:
                category[subcategory].remove(remove_detail)
            else:
                category.remove(remove_detail)
            print(category)
            if subcategory:
                return category[subcategory], f"remove_{remove_detail}" 
            else:
                return category, f"remove_{remove_detail}" 
                

    def _expand_list(self, negotiator, message, details=None, min_additions=1, ask_for_more=True):
        if not details: details = list()
        if min_additions < 1:
            print("Invalid value")
            quit()
        while True:
            new_detail = negotiator.request_word(message, "Name").title()
            print()
            if not new_detail in details:
                details.append(new_detail) 
                if not ask_for_more: break
            else: 
                print(f"{new_detail} already exists.")
            if min_additions == 1:
                if negotiator.confirm_action("Add another?", is_enforced=True):
                    message = "Add addional option"
                    continue
                else:
                    break
            else:
                min_additions -= 1
                message = f"Your new attribute need at least {min_additions} options"
        
        return details, new_detail
    
