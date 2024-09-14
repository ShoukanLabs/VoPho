from phonemizers import mandarin, russian

class Phonemizer:
    def __init__(self, working_path):

        self.working_path = working_path

        # PHONEMIZERS THAT REQUIRE A GPU ARE PLACED HERE
        # This is so we can allocate them a class that will
        # allow us to deallocate and prevent double loading a
        # phonemizer, if you really need to allocate multiple
        # simply instantiate another VoPho.engine.Phonemizer
        self.russian_phonemiser = None