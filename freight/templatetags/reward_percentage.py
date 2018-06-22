from django import template

register = template.Library()

@register.simple_tag
def reward_difference(act, sug):
    return "%.0f" % (100 * (float(act) / sug - 1))
