class PipelineContext:
    def __init__(self):
        self.user_request = ""
        self.language = ""
        self.plan = {}
        self.design = {}
        self.code = ""
        self.issues = []
        self.ready = False
