from zope.interface import Attribute
from z3c.form.interfaces import IForm

class IWizard(IForm):
    """
    A multi-step session-based z3c.form wizard.
    """
    
    steps = Attribute("""
        A sequence of step classes that will be instantiated when the wizard's
        update method is called.
        """)

    activeSteps = Attribute("""
        A sequence of wizard step instances.  Available after the wizard's
        update method has been called.
        """)

    currentStep = Attribute("""
        The wizard step instance currently being displayed.
        """)

    currentIndex = Attribute("""
        The (0-based) index of the current step within the activeSteps sequence.
        """)

    sessionKey = Attribute("""
        Returns the unique session key used by this wizard instance.

        By default, this is a tuple of 'collective.z3cform.wizard' and the URL
        path to the wizard.
        """)

    session = Attribute("""
        The session where data for this wizard is persisted.  Available after
        the wizard's update method has been called.
        """)
    
    onFirstStep = Attribute("""
        Boolean.  True if the first step of the wizard is being displayed.
        """)
    
    onLastStep = Attribute("""
        Boolean.  True if the last step of the wizard is being displayed.
        """)
    
    finished = Attribute("""
        Boolean.  True if the wizard has been completed.
        """)

    def initialize():
        """
        Called the first time a wizard is viewed in a given session.
        
        This method may be used to populate the session with data from some
        source.  When assigning values into the session, make sure you use
        the proper persistent classes (e.g. PersistentDict instead of dict),
        or else changes to subitems may be changed without those changes
        getting persisted.
        
        The default implementation calls the loadSteps method.
        """
    
    def loadSteps(context):
        """
        Loads the wizard session data from a context.
        
        The default implementation calls the 'load' method of each wizard step.
        """
    
    def finish():
        """
        Called when a wizard is successfully completed, after validation of the
        final step.
        
        Use this method to carry out some actions based on the values that have
        been filled out during completion of the wizard.
        
        The default implementation calls the applySteps method.
        """
    
    def applySteps(context):
        """
        Updates a context based on the wizard session data.
        
        The default implementation calls the 'apply' method of each wizard step.
        """
    
    def sync():
        """
        Mark the session as having changed, to ensure that changes get
        persisted.  This is required since we aren't using a
        persistence-aware dictionary class for our session variables.
        """

class IStep(IForm):
    """
    A single step of a z3c.form wizard.
    
    By default, the content accessed by this form will be a PersistentDict
    within the wizard's session, with a key equal to the step's prefix.
    """
    
    label = Attribute('Title displayed at the top of the wizard step.')
    description = Attribute("""
        Description displayed at the top of the wizard step.
        """)
    
    wizard = Attribute('The wizard this step is being used in.')
    
    completed = Attribute("""
        Boolean indicating whether the user should be allowed to move on to the
        next step.  Defaults to True.
        """)

    def applyChanges(data):
        """
        Saves changes from this step to its content (typically a PersistentDict
        in the wizard's session.)
        """

    def load(context):
        """
        Loads the session data for this step based on a context.
        """

    def apply(context):
        """
        Updates a context based on the session data for this step.
        """
