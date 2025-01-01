import re
from django.template import base as template_base

# Add support for multi-line template tags
template_base.tag_re = re.compile(template_base.tag_re.pattern, re.DOTALL)