from collective.z3cform.wizard import wizard
from plone.autoform.base import AutoFields
from plone.z3cform.traversal import FormWidgetTraversal
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest


class AutoWizard(wizard.Wizard, AutoFields):
    """Wizard based on a plone.autoform schema.
    
    Steps will be automatically generated from the schema's fieldsets.
    """
    schema = None
    
    def createStepsFromGroups(self):
        steps = []
        for g in self.groups:
            class StepFromGroup(wizard.Step):
                __name__ = g.__name__
                label = g.label
                description = g.description
                prefix = "%s%s." % (self.prefix, g.__name__)
                fields = g.fields
            steps.append(StepFromGroup)
        self.steps = steps

    def update(self):
        self.updateFieldsFromSchemata()
        self.createStepsFromGroups()
        super(AutoWizard, self).update()
        self.groups = self.activeSteps


class AutoWizardWidgetTraversal(FormWidgetTraversal):
    """Allow traversal to widgets via the ++widget++ namespace.
    """
    adapts(AutoWizard, IBrowserRequest)

    def _prepareForm(self):
        self.context.update()
        for step in self.context.activeSteps:
            step.update()
        return self.context
