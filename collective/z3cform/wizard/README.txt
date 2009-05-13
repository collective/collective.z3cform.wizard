Introduction
============

This library implements a simple z3c.form-based wizard.  The wizard is composed
of multiple steps.  Each step is a form.  Data is stored in a session until
the user clicks the Finish button on the last step.

In order to make good use of this library you'll need to be reasonably familiar
with z3c.form first.  Here are some places to start:

 * Official documentation: http://docs.zope.org/z3c.form
 
 * Slides from Stephan Richter's tutorial at Plone Conference 2008: http://svn.zope.org/*checkout*/z3c.talk/trunk/Z3CForms/Z3CForms.html?rev=92118
 

Wizard Step
-----------

A wizard step is a normal z3c.form form with a few additional features.

By default, the content accessed by this form will be a dictionary
within the wizard's session, with a key equal to the step's prefix.

Additional attributes:

  wizard
    The wizard this step is being used in.

  completed
    Boolean indicating whether the user should be allowed to move on to the
    next step.  Defaults to True.  Override this with a property if you need
    custom logic.

Additional methods:

  applyChanges(data)
    Saves changes from this step to its content (typically a PersistentDict
    in the wizard's session.)

  load(context):
    Loads the session data for this step based on a context.

  apply(context):
    Updates a context based on the session data for this step.


Wizard
------

The wizard is also a form, with a list of steps and built-in logic for
moving between those steps.

Class attributes.  Override these to affect how the wizard behaves:

  steps
    A sequence of step classes that will be instantiated when the wizard's
    update method is called.

  sessionKey
    Returns the unique session key used by this wizard instance. By default,
    this is a tuple of 'collective.z3cform.wizard' and the URL
    path to the wizard.

Attributes set during the update method:

  activeSteps
    A sequence of wizard step instances.

  currentStep
    The wizard step instance currently being displayed.

  currentIndex
    The (0-based) index of the current step within the activeSteps sequence.

  session
    The session where data for this wizard is persisted.

  onFirstStep
    Boolean.  True if the first step of the wizard is being displayed.

  onLastStep
    Boolean.  True if the last step of the wizard is being displayed.

  finished
    Boolean.  True if the wizard has been completed.

Methods:

  initialize()
    Called the first time a wizard is viewed in a given session.
      
    This method may be used to populate the session with data from some
    source.
      
    The default implementation calls the loadSteps method.
  
  loadSteps(context)
    Loads the wizard session data from a context.
      
    The default implementation calls the 'load' method of each wizard step.
  
  finish()
    Called when a wizard is successfully completed, after validation of the
    final step.
      
    Use this method to carry out some actions based on the values that have
    been filled out during completion of the wizard.
      
    The default implementation calls the applySteps method.
  
  applySteps(context)
    Updates a context based on the wizard session data.
      
    The default implementation calls the 'apply' method of each wizard step.
  
  sync()
    Mark the session as having changed, to ensure that changes get
    persisted.  This is required since we aren't using a
    persistence-aware dictionary class for our session variables.


Compatibility
=============

This package has been tested in Zope 2.10 with Plone 3.3.

It should be pretty easy to get it to work in other environments supported by
z3c.form, such as Zope 3, but I'll need someone familiar with those environments
to tell me how sessions work there, for example.

Credits
=======

This package is inspired by and based on the non-session-based z3c.form wizard
included in the collective.singing package, which was implemented by Daniel
Nouri.

Session support, miscellaneous improvements, and repackaging by David Glick.
