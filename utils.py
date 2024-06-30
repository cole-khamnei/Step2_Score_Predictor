import dill as pickle

# ------------------------------------------------------------------- #
# --------------------         Functions         -------------------- #
# ------------------------------------------------------------------- #

def pickle_load(filename: str):
    """ """
    with open(filename, "rb") as file:
        return pickle.load(file)

    
def pickle_write(filename: str, obj):
    """ """
    with open(filename, "wb") as file:
        return pickle.dump(obj, file)


def is_interactive() -> bool:
    """ """
    import __main__ as main
    return not hasattr(main, '__file__')


# ------------------------------------------------------------------- #
# --------------------            End            -------------------- #
# ------------------------------------------------------------------- #