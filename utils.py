def get_bond_type(atom1, atom2):
    delta_en = abs(atom1.electronegativity - atom2.electronegativity)
    if delta_en >= 1.8:
        return 'Jonbindning'
    elif 0.9 <= delta_en < 1.8:
        return 'Polär kovalent bindning'
    elif 0.4 <= delta_en < 0.9:
        return 'Svagt polär kovalent bindning'
    else:
        return 'Ren kovalent bindning'
