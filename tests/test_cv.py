from cmipld.cv import CV
from cmipld.cv import CMIP6Plus_CV


def test_univ_cv():
    universe_cv = CV()
    assert(universe_cv.local == False)


def test_univ_cv_get_term():
    universe_cv = CV()
    univ_ipsl = universe_cv.get_term("institution","ipsl")
    assert("IPSL" in univ_ipsl.acronyms)

def test_project_cv_get_term():
    project_cv = CMIP6Plus_CV()
    project_ipsl = project_cv.get_term("institution_id","ipsl")
    assert("IPSL" in project_ipsl.acronyms)
