class Gdk9Error(Exception):
  """Base exception for Gdk9 CLI."""


class ConfigError(Gdk9Error):
  """Configuration file or principle load error."""


class InputError(Gdk9Error):
  """Invalid input provided by user."""


class OptimizationError(Gdk9Error):
  """Unable to find or apply an attunement/optimization plan."""

