from sqlalchemy import Column, Boolean, text


class Printable:
    """Mixin Class that allows to handle printable items"""

    queued_for_printing = Column(
        Boolean, default=False, nullable=False, server_default=text("0")
    )

    def set_for_printing(self):
        self.queued_for_printing = True

    def unset_for_printing(self):
        self.queued_for_printing = False
