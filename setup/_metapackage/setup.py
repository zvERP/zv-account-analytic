import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-zverp-account-analytic",
    description="Meta package for zverp-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_analytic_responsible>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
