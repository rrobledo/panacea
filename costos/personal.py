def calcular_liquidacion(sueldo_bruto, descuento_sindical=0.0, alicuota_art=5.0):
    """
    Calcula sueldo neto y costo empresa a partir del sueldo bruto.

    :param sueldo_bruto: Monto bruto en pesos.
    :param descuento_sindical: Porcentaje de descuento sindical (ej: 2 para 2%).
    :param alicuota_art: Porcentaje ART a cargo del empleador.
    :return: Diccionario con resultados.
    """

    # Descuentos al empleado
    descuento_jubilacion = sueldo_bruto * 0.11
    descuento_obra_social = sueldo_bruto * 0.03
    descuento_pami = sueldo_bruto * 0.03
    descuento_sindicato = sueldo_bruto * (descuento_sindical / 100)

    total_descuentos = (
            descuento_jubilacion +
            descuento_obra_social +
            descuento_pami +
            descuento_sindicato
    )

    sueldo_neto = sueldo_bruto - total_descuentos

    # Cargas patronales
    contrib_jubilacion = sueldo_bruto * 0.1077
    contrib_obra_social = sueldo_bruto * 0.06
    contrib_pami = sueldo_bruto * 0.015
    contrib_asignaciones = sueldo_bruto * 0.0444
    contrib_fondo_empleo = sueldo_bruto * 0.0111
    contrib_art = sueldo_bruto * (alicuota_art / 100)

    total_cargas_patronales = (
            contrib_jubilacion +
            contrib_obra_social +
            contrib_pami +
            contrib_asignaciones +
            contrib_fondo_empleo +
            contrib_art
    )

    costo_total_empresa = sueldo_bruto + total_cargas_patronales

    return {
        "sueldo_bruto": sueldo_bruto,
        "descuento_jubilacion": descuento_jubilacion,
        "descuento_obra_social": descuento_obra_social,
        "descuento_pami": descuento_pami,
        "descuento_sindicato": descuento_sindicato,
        "total_descuentos": total_descuentos,
        "sueldo_neto": sueldo_neto,
        "contrib_jubilacion": contrib_jubilacion,
        "contrib_obra_social": contrib_obra_social,
        "contrib_pami": contrib_pami,
        "contrib_asignaciones": contrib_asignaciones,
        "contrib_fondo_empleo": contrib_fondo_empleo,
        "contrib_art": contrib_art,
        "total_cargas_patronales": total_cargas_patronales,
        "costo_total_empresa": costo_total_empresa,
        "costo_hora": costo_total_empresa / (44 * 5)
    }


# Ejemplo de uso:
if __name__ == "__main__":
    bruto = float(input("Ingrese el sueldo bruto: "))
    sindical = float(input("Porcentaje descuento sindical (0 si no hay): "))
    art = float(input("Alicuota ART (%): "))

    resultado = calcular_liquidacion(bruto, descuento_sindical=sindical, alicuota_art=art)

    print("\n==== Liquidación Empleado ====")
    print(f"Sueldo Bruto: ${resultado['sueldo_bruto']:.2f}")
    print(f"Descuento Jubilación: ${resultado['descuento_jubilacion']:.2f}")
    print(f"Descuento Obra Social: ${resultado['descuento_obra_social']:.2f}")
    print(f"Descuento PAMI: ${resultado['descuento_pami']:.2f}")
    print(f"Descuento Sindical: ${resultado['descuento_sindicato']:.2f}")
    print(f"Total Descuentos: ${resultado['total_descuentos']:.2f}")
    print(f"Sueldo Neto: ${resultado['sueldo_neto']:.2f}")

    print("\n==== Cargas Patronales ====")
    print(f"Contribución Jubilación: ${resultado['contrib_jubilacion']:.2f}")
    print(f"Contribución Obra Social: ${resultado['contrib_obra_social']:.2f}")
    print(f"Contribución PAMI: ${resultado['contrib_pami']:.2f}")
    print(f"Asignaciones Familiares: ${resultado['contrib_asignaciones']:.2f}")
    print(f"Fondo Nacional Empleo: ${resultado['contrib_fondo_empleo']:.2f}")
    print(f"ART: ${resultado['contrib_art']:.2f}")
    print(f"Total Cargas Patronales: ${resultado['total_cargas_patronales']:.2f}")

    print(f"\nCosto Total Empresa: ${resultado['costo_total_empresa']:.2f}")
    print(f"\nCosto Hora: ${resultado['costo_hora']:.2f}")

