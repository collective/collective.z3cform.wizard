from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.z3cform.wizard',
      version=version,
      description="This is a library for creating multi-page wizards using z3c.form.  Values are stored in a session until the wizard is finished.",
      long_description=open(os.path.join('collective', 'z3cform', 'wizard', 'README.txt')).read() + "\n" +
                       open(os.path.join('collective', 'z3cform', 'wizard', 'HISTORY.txt')).read() + "\n" +
                       open(os.path.join('collective', 'z3cform', 'wizard', 'wizard.txt')).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Zope2',
          'Framework :: Plone',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          ],
      keywords='z3c.form wizard session',
      author='David Glick',
      author_email='davidglick@onenw.org',
      url='http://svn.plone.org/svn/collective/collective.z3cform.wizard/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.z3cform',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
