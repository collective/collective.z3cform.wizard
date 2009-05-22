"""
A simple wizard for z3c.form that keeps values in the session
until the wizard is finished.

Inspired by and based on the non-session-based wizard in
collective.singing

collective.z3cform.wizard
Copyright (C) 2009 ONE/Northwest

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import zope.component
from zope.interface import implements
from zope.app.pagetemplate import viewpagetemplatefile
from z3c.form import button, field, form, interfaces

from collective.z3cform.wizard import utils
from collective.z3cform.wizard.interfaces import IWizard, IStep
from collective.z3cform.wizard.i18n import MessageFactory as _

WIZARD_SESSION_KEY = 'collective.z3cform.wizard'

# slight modification of the normal applyChanges method from z3c.form.form,
# to make it not break if there's no value set yet
def applyChanges(form, content, data):
    changes = {}
    for name, field in form.fields.items():
        # If the field is not in the data, then go on to the next one
        if name not in data:
            continue
        # Get the datamanager and get the original value
        dm = zope.component.getMultiAdapter(
            (content, field.field), interfaces.IDataManager)
        oldValue = dm.query()
        # Only update the data, if it is different
        if oldValue != data[name]:
            dm.set(data[name])
            # Record the change using information required later
            changes.setdefault(dm.field.interface, []).append(name)
    return changes

class Step(utils.OverridableTemplate, form.Form):
    """
    Base class for a wizard step implementing the IStep interface.
    
    Subclasses will typically want to override at least the fields attribute.
    """
    implements(IStep)
    
    index = viewpagetemplatefile.ViewPageTemplateFile('wizard-step.pt')
    subforms = ()
    label = u""
    description = u""
    
    wizard = None
    completed = True

    def __init__(self, context, request, wizard):
        super(Step, self).__init__(context, request)
        self.wizard = wizard
    
    def getContent(self):
        return self.request.SESSION[self.wizard.sessionKey].setdefault(self.prefix, {})

    def applyChanges(self, data):
        content = self.getContent()
        applyChanges(self, content, data)
        self.wizard.sync()
    
    def load(self, context, **kw):
        pass
    
    def apply(self, context, **kw):
        pass

class Wizard(utils.OverridableTemplate, form.Form):
    """
    Abstract class for a wizard implementing the IWizard interface.
    
    Subclasses must provide at least the finish method.
    """
    
    implements(IWizard)

    successMessage = _(u"Information submitted successfully.")
    formErrorsMessage = _(u"There were errors.")

    index = viewpagetemplatefile.ViewPageTemplateFile('wizard.pt')
    
    steps = () # Set this to be form classes
    label = u""
    description = u""
    ignoreContext = True
    fields = field.Fields()

    currentStep = None
    currentIndex = None
    finished = False

    @property
    def sessionKey(self):
        try:
            path = list(self.context.getPhysicalPath())
        except:
            path = []
        path.append(self.__name__)
        return (WIZARD_SESSION_KEY, tuple(path))

    def update(self):
        # initialize session
        sessionKey = self.sessionKey
        if not self.request.SESSION.has_key(sessionKey):
            self.request.SESSION[sessionKey] = {}
        if self.request['HTTP_REFERER'].startswith('http') and self.request['ACTUAL_URL'] != self.request['HTTP_REFERER']:
            self.request.SESSION[sessionKey] = {}
        self.session = self.request.SESSION[sessionKey]

        # initialize steps
        self.activeSteps = []
        for step in self.steps:
            step = step(self.context, self.request, self)
            self.activeSteps.append(step)

        # if this wizard hasn't been loaded yet in this session,
        # load the data
        if not len(self.session):
            self.initialize()
            self.sync()

        self.currentStep = None
        self.currentIndex = self.session.setdefault('step', 0)
        self.updateCurrentStep()

        self.updateActions()
        self.actions.execute()

    def updateActions(self):
        """
        Allow the current step to determine whether the wizard navigation is enabled.
        """
        form.Form.updateActions(self)
        if not self.currentStep.completed:
            if self.onLastStep:
                self.actions['finish'].disabled = 'disabled'
            else:
                self.actions['continue'].disabled = 'disabled'

    def updateCurrentStep(self):
        self.currentStep = self.activeSteps[self.currentIndex]
        self.currentStep.update()

    @property
    def onFirstStep(self):
        return self.currentIndex == 0

    @button.buttonAndHandler(u'Back',
                             name='back',
                             condition=lambda form:not form.onFirstStep)
    def handleBack(self, action):
        data, errors = self.currentStep.extractData()
        if errors:
            self.status = self.formErrorsMessage
        else:
            self.currentStep.applyChanges(data)
            
            self.currentIndex = currentIndex = self.currentIndex - 1
            self.session['step'] = currentIndex
            self.sync()
            self.updateCurrentStep()
            
            # Back can change the conditions for the finish button,
            # so we need to reconstruct the button actions, since we
            # do not redirect.
            self.updateActions()

    @property
    def onLastStep(self):
        return self.currentIndex == len(self.steps) - 1

    @button.buttonAndHandler(u'Continue',
                             name='continue',
                             condition=lambda form:not form.onLastStep)
    def handleContinue(self, action):
        data, errors = self.currentStep.extractData()
        if errors:
            self.status = self.formErrorsMessage
        else:
            self.currentStep.applyChanges(data)
            
            self.currentIndex = currentIndex = self.currentIndex + 1
            self.session['step'] = currentIndex
            self.sync()
            self.updateCurrentStep()

            # Proceed can change the conditions for the finish button,
            # so we need to reconstruct the button actions, since we
            # do not redirect.
            self.updateActions()

    @button.buttonAndHandler(u'Finish',
                             name='finish',
                             condition=lambda form:form.onLastStep)
    def handleFinish(self, action):
        data, errors = self.currentStep.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        else:
            self.status = self.successMessage
            self.finished = True
        self.currentStep.applyChanges(data)
        self.finish()
        # clear out the session
        self.request.SESSION[self.sessionKey] = {}
        self.sync()

    def initialize(self):
        self.loadSteps(self.context)

    def loadSteps(self, context):
        for step in self.activeSteps:
            if hasattr(step, 'load'):
                step.load(context)
    
    def finish(self):
        self.applySteps(self.context)
    
    def applySteps(self, context):
        for step in self.activeSteps:
            if hasattr(step, 'apply'):
                step.apply(context)

    def sync(self):
        self.request.SESSION._p_changed = True
