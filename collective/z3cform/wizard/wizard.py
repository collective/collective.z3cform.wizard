"""
A simple wizard for z3c.form that keeps values in the session
until the wizard is finished.

Inspired by and based on the non-session-based wizard in
collective.singing

collective.z3cform.wizard
Copyright (C) 2010 Groundwire

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
from z3c.form import button, field, form, interfaces, group
from Products.statusmessages.interfaces import IStatusMessage

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

    @property
    def available(self):
        if self.prefix in self.request.SESSION[self.wizard.sessionKey]:
            return True
        return False

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

    def update(self):
        session = self.wizard.session
        data = session.get(self.prefix, None)
        if data is None:
            self.load(self.wizard.context)
            self.wizard.sync()
        super(Step, self).update()


class GroupStep(group.GroupForm, Step):
    def applyChanges(self, data):
        """ Override to make sure we use the wizard's session storage for group fields """
        content = self.getContent()
        changed = applyChanges(self, content, data)
        for group in self.groups:
            groupContent = group.getContent()
            groupChanged = applyChanges(group, groupContent, data)
            for interface, names in groupChanged.items():
                changed[interface] = changed.get(interface, []) + names

        return changed


class Wizard(utils.OverridableTemplate, form.Form):
    """
    Abstract class for a wizard implementing the IWizard interface.

    Subclasses must provide at least the finish method.
    """

    implements(IWizard)

    successMessage = _(u"Information submitted successfully.")
    formErrorsMessage = _(u"There were errors.")
    clearMessage = _(u"Form cleared.")

    index = viewpagetemplatefile.ViewPageTemplateFile('wizard.pt')

    steps = () # Set this to be form classes
    label = u""
    description = u""
    ignoreContext = True
    fields = field.Fields()

    currentStep = None
    currentIndex = None
    finished = False
    validate_back = True

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
        # Reset session if we came from a URL different from that of the wizard,
        # unless it's the URL that's used during z3cform inline validation.
        referer = self.request.get('HTTP_REFERER', '')
        url = self.request.get('ACTUAL_URL', '')
        if referer.startswith('http') and 'kss_z3cform_inline_validation' not in url:
            if not utils.location_is_equal(url, referer):
                self.request.SESSION[sessionKey] = {}
        self.session = self.request.SESSION[sessionKey]

        self.updateActiveSteps()

        # if this wizard hasn't been loaded yet in this session,
        # load the data
        if not len(self.session):
            self.initialize()
            self.sync()

        self.jumpToCurrentStep()

        self.updateActions()
        self.actions.execute()
        self.updateWidgets()

    def updateActiveSteps(self):
        self.activeSteps = []
        for step in self.steps:
            step = step(self.context, self.request, self)
            self.activeSteps.append(step)

    def jumpToCurrentStep(self):
        self.updateCurrentStep(self.session.setdefault('step', 0))
        if 'step' in self.request.form:
            self.jump(self.request.form['step'])

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

    def updateCurrentStep(self, index):
        self.currentIndex = index
        self.session['step'] = self.currentIndex
        self.sync()
        self.currentStep = self.activeSteps[self.currentIndex]
        self.currentStep.update()

    @property
    def onLastStep(self):
        return self.currentIndex == len(self.steps) - 1

    def showContinue(self):
        return not self.onLastStep

    @button.buttonAndHandler(_(u'Continue'),
                             name='continue',
                             condition=lambda form: form.showContinue())
    def handleContinue(self, action):
        messages = IStatusMessage(self.request)
        data, errors = self.currentStep.extractData()
        if errors:
            self.status = self.formErrorsMessage
            messages.addStatusMessage(self.status, type="error")
        else:
            self.currentStep.applyChanges(data)
            self.updateCurrentStep(self.currentIndex + 1)

            # Proceed can change the conditions for the finish button,
            # so we need to reconstruct the button actions, since we
            # do not redirect.
            self.updateActions()

    @property
    def allStepsFinished(self):
        for step in self.activeSteps:
            if not step.available:
                return False
        return True

    def showFinish(self):
        return self.allStepsFinished or self.onLastStep

    @button.buttonAndHandler(_(u'Finish'),
                             name='finish',
                             condition=lambda form:form.showFinish())
    def handleFinish(self, action):
        messages = IStatusMessage(self.request)
        data, errors = self.currentStep.extractData()
        if errors:
            self.status = self.formErrorsMessage
            messages.addStatusMessage(self.status, type="error")
            return
        else:
            self.status = self.successMessage
            self.finished = True
            messages.addStatusMessage(self.status, type="info")
        self.currentStep.applyChanges(data)
        self.finish()
        # clear out the session
        self.request.SESSION[self.sessionKey] = {}
        self.sync()

    @property
    def onFirstStep(self):
        return self.currentIndex == 0

    def showBack(self):
        return not self.onFirstStep

    @button.buttonAndHandler(_(u'Back'),
                             name='back',
                             condition=lambda form:form.showBack())
    def handleBack(self, action):
        messages = IStatusMessage(self.request)

        if self.validate_back:
            # if true, only allow navigating back if the current
            # step validates
            data, errors = self.currentStep.extractData()
            if errors:
                self.status = self.formErrorsMessage
                messages.addStatusMessage(self.status, type="error")
                return
            self.currentStep.applyChanges(data)

        self.updateCurrentStep(self.currentIndex - 1)

        # Back can change the conditions for the finish button,
        # so we need to reconstruct the button actions, since we
        # do not redirect.
        self.updateActions()

    def showClear(self):
        values = [v for v in self.session.values() if isinstance(v, dict)]
        if len(values) > 1:
            return True
        for value in values:
            if value:
                return True
        return False

    @button.buttonAndHandler(_(u'Clear'),
                             name='clear',
                             condition=lambda form:form.showClear())
    def handleClear(self, action):
        self.session.clear()
        self.sync()
        self.status = self.clearMessage
        self.updateActiveSteps()
        self.updateCurrentStep(0)
        self.updateActions()
        self.currentStep.ignoreRequest = True
        self.currentStep.update()

    def jump(self, step_idx):
        # make sure target is available
        try:
            target_step = self.activeSteps[step_idx]
        except (KeyError, TypeError):
            return
        if not target_step.available:
            return

        self.updateCurrentStep(step_idx)
        self.updateActions()

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

    @property
    def absolute_url(self):
        return self.context.absolute_url() + '/' + self.__name__
