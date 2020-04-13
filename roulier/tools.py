def get_subclass(base_class, carrier_type, action):
    final_subclasses = []
    work = [base_class]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            sublcasses = child.__subclasses__()
            if sublcasses:
                work += sublcasses
                continue
            if child._carrier_type != carrier_type or child._action and action not in child._action:
                continue
            if child not in final_subclasses:
                final_subclasses.append(child)
    if not final_subclasses:
        return base_class
    elif len(final_subclasses) > 1:
        for final_subclass in final_subclasses:
            if final_subclass._action == action:
                return final_subclass
    return final_subclasses[0]
