"""Import every ORM model once so SQLAlchemy can resolve relationships."""

import app.audit.models  # noqa: F401
import app.auth.models  # noqa: F401
import app.products.models  # noqa: F401
import app.users.models  # noqa: F401
