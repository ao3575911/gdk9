"""A minimal example plugin illustrating the plugin API."""

class ExamplePlugin:
    name = "example"

    def setup(self, config):
        self.config = config or {}
        print("ExamplePlugin.setup called with", self.config)

    def run(self, *args, **kwargs):
        print("ExamplePlugin.run called with", args, kwargs)
        return {"status": "ok", "args": args, "kwargs": kwargs}