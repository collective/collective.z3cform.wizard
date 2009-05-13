class OverridableTemplate(object):
    """Subclasses of this class must set the template they want to use
    as the default template as the ``index`` attribute, not the
    ``template`` attribute that's normally used for forms.
    
    Users of this package may override the template used by one of the
    forms by using the ``browser`` directive and specifying their own
    template.
    """
    @property
    def template(self):
        return self.index
