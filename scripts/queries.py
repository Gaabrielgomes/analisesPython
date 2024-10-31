razão_básico = """
WITH Razao_Geral AS (
    SELECT 
        lancto.fili_lan AS FILIAL, 
        lancto.data_lan AS DATA, 
        lancto.dorig_lan AS DATA_ORIG, 
        lancto.cdeb_lan AS DEBITO, 
        lancto.ccre_lan AS CREDITO, 
        lancto.chis_lan AS HISTORICO, 
        lancto.vlor_lan AS VALOR
    FROM 
        bethadba.ctlancto lancto
    LEFT JOIN 
        bethadba.ctcontas contas ON lancto.codi_emp = contas.codi_emp AND lancto.cdeb_lan = contas.codi_cta
    WHERE 
        lancto.codi_emp IN (?)
        AND lancto.data_lan BETWEEN CONVERT(DATE, ?, 112) AND CONVERT(DATE, ?, 112)
        AND contas.codi_cta = ?
    
    UNION ALL 

    SELECT 
        lancto.fili_lan, 
        lancto.data_lan, 
        lancto.dorig_lan, 
        lancto.cdeb_lan, 
        lancto.ccre_lan, 
        lancto.chis_lan, 
        (lancto.vlor_lan * -1) AS VALOR
    FROM 
        bethadba.ctlancto lancto
    LEFT JOIN 
        bethadba.ctcontas contas ON lancto.codi_emp = contas.codi_emp AND lancto.ccre_lan = contas.codi_cta
    WHERE 
        lancto.codi_emp IN (?) 
        AND lancto.data_lan BETWEEN CONVERT(DATE, ?, 112) AND CONVERT(DATE, ?, 112)
        AND contas.codi_cta = ?
)
SELECT * FROM Razao_Geral 
ORDER BY FILIAL, DATA_ORIG DESC;
"""

razão_geral = """
WITH Razao_Geral AS (
    SELECT 
        lancto.fili_lan AS FILIAL, 
        lancto.data_lan AS DATA, 
        lancto.dorig_lan AS DATA_ORIG, 
        lancto.cdeb_lan AS DEBITO, 
        lancto.ccre_lan AS CREDITO, 
        REPLACE(lancto.chis_lan, CHAR(2), '') AS HISTORICO, 
        lancto.vlor_lan AS VALOR
    FROM 
        bethadba.ctlancto lancto
    LEFT JOIN 
        bethadba.ctcontas contas ON lancto.codi_emp = contas.codi_emp AND lancto.cdeb_lan = contas.codi_cta
    WHERE 
        lancto.codi_emp IN (?)
        AND lancto.data_lan BETWEEN CONVERT(DATE, ?, 112) AND CONVERT(DATE, ?, 112)
        AND contas.codi_cta LIKE (? || '%')
    
    UNION ALL 

    SELECT 
        lancto.fili_lan, 
        lancto.data_lan, 
        lancto.dorig_lan, 
        lancto.cdeb_lan, 
        lancto.ccre_lan, 
        REPLACE(lancto.chis_lan, CHAR(2), '') AS HISTORICO, 
        (lancto.vlor_lan * -1) AS VALOR
    FROM 
        bethadba.ctlancto lancto
    LEFT JOIN 
        bethadba.ctcontas contas ON lancto.codi_emp = contas.codi_emp AND lancto.ccre_lan = contas.codi_cta
    WHERE 
        lancto.codi_emp IN (?)
        AND lancto.data_lan BETWEEN CONVERT(DATE, ?, 112) AND CONVERT(DATE, ?, 112)
        AND contas.codi_cta LIKE (? || '%')
)
SELECT * FROM Razao_Geral 
ORDER BY FILIAL, DATA_ORIG DESC;
"""

obter_cliente = """
    SELECT 
        razao_emp, 
        codi_emp 
    FROM bethadba.geempre 
    WHERE stat_emp <> 'I'
    AND LOWER(razao_emp) LIKE LOWER('%' || ? || '%') 
    ORDER BY razao_emp;
    """

obter_saldo = """
WITH SALDO_ANT_DEB AS (
    SELECT SUM(lancto.vlor_lan) AS Soma
    FROM bethadba.ctlancto lancto
    LEFT JOIN bethadba.ctcontas contas ON lancto.codi_emp = contas.codi_emp AND lancto.cdeb_lan = contas.codi_cta
    WHERE lancto.codi_emp IN (?)
    AND lancto.data_lan <= DATEADD(MONTH, -1, CONVERT(DATE, ?, 112))
    AND contas.codi_cta = ?
), 
SALDO_ANT_CRED AS (
    SELECT SUM(lancto.vlor_lan) AS Soma
    FROM bethadba.ctlancto lancto
    LEFT JOIN bethadba.ctcontas contas ON lancto.codi_emp = contas.codi_emp AND lancto.ccre_lan = contas.codi_cta
    WHERE lancto.codi_emp IN (?)
    AND lancto.data_lan <= DATEADD(MONTH, -1, CONVERT(DATE, ?, 112))
    AND contas.codi_cta = ?
)
SELECT (SELECT Soma FROM SALDO_ANT_CRED) - (SELECT Soma FROM SALDO_ANT_DEB) AS [SALDO ANTERIOR];
"""

obter_saldo_tipoconta = """
WITH SALDO_ANT_DEB AS (
    SELECT SUM(lancto.vlor_lan) AS Soma
    FROM bethadba.ctlancto lancto
    LEFT JOIN bethadba.ctcontas contas ON lancto.codi_emp = contas.codi_emp AND lancto.cdeb_lan = contas.codi_cta
    WHERE lancto.codi_emp IN (?)
    AND lancto.data_lan <= DATEADD(MONTH, -1, CONVERT(DATE, ?, 112))
    AND contas.codi_cta LIKE(? || '%')
), 
SALDO_ANT_CRED AS (
    SELECT SUM(lancto.vlor_lan) AS Soma
    FROM bethadba.ctlancto lancto
    LEFT JOIN bethadba.ctcontas contas ON lancto.codi_emp = contas.codi_emp AND lancto.ccre_lan = contas.codi_cta
    WHERE lancto.codi_emp IN (?)
    AND lancto.data_lan <= DATEADD(MONTH, -1, CONVERT(DATE, ?, 112))
    AND contas.codi_cta LIKE(? || '%')
)
SELECT (SELECT Soma FROM SALDO_ANT_CRED) - (SELECT Soma FROM SALDO_ANT_DEB) AS [SALDO ANTERIOR];
"""
