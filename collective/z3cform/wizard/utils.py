from urlparse import urlsplit

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

def location_is_equal(url1, url2):
    proto1, host1, path1, query1, fragment1 = urlsplit(url1)
    proto2, host2, path2, query2, fragment2 = urlsplit(url2)
    return (proto1 == proto2) & (host1 == host2) & (path1 == path2)
