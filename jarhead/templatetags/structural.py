from classytags.core import Tag, Options
from classytags.arguments import Argument
from django import template

register = template.Library()

@register.tag
class Nav(Tag):
    '''
    Render the sidebar navigation
    '''
    name = 'nav'
    options = Options(
        Argument('hub', required=True, resolve=True),
        blocks=[('enter_submenu', 'item'), ('end_submenu', 'enter_submenu'), ('endnav', 'end_submenu')],
    )

    def render_tag(self, context, hub, item, **kwargs):
        output = ""
        for x in hub.root_navigations(context['request']):
            context.push()
            context['nav_item'] = x
            if x.step_type in kwargs:
                output += kwargs[x.step_type].render(context)
            else:
                output += item.render(context)
            context.pop()
        return output



@register.tag
class RenderBlocks(Tag):
    '''
    Render the navigation as blocks in a hub
    '''
    name = 'render_blocks'
    options = Options(
        Argument('hub', required=True, resolve=True),
        blocks=[('enter_submenu', 'item'), ('end_submenu', 'enter_submenu'), ('endrender_blocks', 'end_submenu')],
    )

    def render_tag(self, context, hub, item, **kwargs):
        output = ""
        level = 0
        for x in hub.root_navigations(context['request']):
            context.push()
            context['nav_item'] = x
            if x.step_type in kwargs:
                output += kwargs[x.step_type].render(context)
                if x.step_type == 'enter_submenu':
                    level += 1
                elif x.step_type == 'end_submenu':
                    level -= 1
            else:
                if level > 0: #do not output the top-level "dashboard" item
                    output += item.render(context)
            context.pop()
        return output





