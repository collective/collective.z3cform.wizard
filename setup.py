from setuptools import setup, find_packages
import os

version = '1.4.7'

DOCTESTS_PATH = os.path.join('collective', 'z3cform', 'wizard')

setup(name='collective.z3cform.wizard',
      version=version,
      description="This is a library for creating multi-page wizards using "
          "z3c.form. Values are stored in a session until the wizard is "
          "finished.",
      long_description=open('README.txt').read() + "\n" +
                       open('CHANGES.txt').read() + "\n" +
                       open(os.path.join(DOCTESTS_PATH, 'wizard.txt')).read()
                       + "\n" +
                       open(os.path.join(DOCTESTS_PATH, 'dynamic_wizard.txt')
                           ).read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Framework :: Zope2',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          ],
      keywords='z3c.form wizard session',
      author='David Glick',
      author_email='davidglick@groundwire.org',
      url=(
        'http://svn.plone.org/svn/collective/collective.z3cform.wizard/trunk'),
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.z3cform>=0.7.5',
          'Products.statusmessages',
          'Zope2',
          # -*- Extra requirements: -*-
      ],
      extras_require=dict(
          test=['plone.autoform', 'z3c.form[test]'],
          autowizard=['plone.autoform'],
          ),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
