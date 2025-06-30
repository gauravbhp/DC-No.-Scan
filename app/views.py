from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
import datetime
import re

def extract_int(value):
    if value is None:
        return 0
    match = re.search(r'\d+', str(value))
    if match:
        return int(match.group())
    return 0

# def scanner(request):
#     trips = []
#     error_message = None

#     if request.method == 'POST':
#         qr_input = request.POST.get('qr_code_value')

#         if qr_input:
#             with connection.cursor() as cursor:
#                 # First check if it's a DC (Internal Document)
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM DB2INST1.INTERNALDOCUMENT 
#                     WHERE PROVISIONALCODE = %s
#                 """, [qr_input])
#                 is_dc = cursor.fetchone()[0] > 0

#                 if is_dc:
#                     return handle_dc_scan(cursor, qr_input, request)

#                 # Try Commercial Invoice via GRDETAILS
#                 cursor.execute("""
#                     SELECT CI.CODE
#                     FROM DB2INST1.COMMERCIALINVOICE CI
#                     LEFT JOIN DB2INST1.SKPCOMMERCIALINVOICE DC
#                         ON DC.COMPANYCODE = CI.COMPANYCODE
#                         AND DC.DIVISIONCODE = CI.DIVISIONCODE
#                         AND DC.CODE = CI.CODE
#                     WHERE CI.COMPANYCODE = '100'
#                       AND DC.GRDETAILS = %s
#                 """, [qr_input])
#                 commercial_invoice_row = cursor.fetchone()

#                 if commercial_invoice_row:
#                     commercial_invoice_code = commercial_invoice_row[0]
#                     return handle_commercial_invoice_by_code(cursor, commercial_invoice_code, request)

#                 # Check if it's a Commercial Invoice by CHALLANNO
#                 cursor.execute("""
#                     SELECT CODE FROM DB2INST1.COMMERCIALINVOICE 
#                     WHERE CHALLANNO = %s
#                     FETCH FIRST 1 ROWS ONLY
#                 """, [qr_input])
#                 commercial_invoice_row = cursor.fetchone()

#                 if commercial_invoice_row:
#                     commercial_invoice_code = commercial_invoice_row[0]
#                     return handle_commercial_invoice_by_code(cursor, commercial_invoice_code, request)

#                 # Check if it's a Plant Invoice by CHALLANNO
#                 cursor.execute("""
#                     SELECT CODE FROM DB2INST1.PLANTINVOICE 
#                     WHERE CHALLANNO = %s
#                     FETCH FIRST 1 ROWS ONLY
#                 """, [qr_input])
#                 plant_invoice_row = cursor.fetchone()

#                 if plant_invoice_row:
#                     plant_invoice_code = plant_invoice_row[0]
#                     return handle_plant_invoice(cursor, plant_invoice_code, request)

#                 error_message = "Details Not Found! Invalid QR Code."

#     return render(request, 'pages/scan.html', {
#         'trips': trips,
#         'error_message': error_message
#     })

def scanner(request):
    trips = []
    error_message = None

    if request.method == 'POST':
        qr_input = request.POST.get('qr_code_value')
        data = request.POST.dict()
        print("Received POST data:", data)
        if qr_input:
            with connection.cursor() as cursor:
                # First check if it's a DC (Internal Document)
                cursor.execute("""
                    SELECT COUNT(*) FROM DB2INST1.INTERNALDOCUMENT 
                    WHERE PROVISIONALCODE = %s
                """, [qr_input])
                is_dc = cursor.fetchone()[0] > 0

                if is_dc:
                    return handle_dc_scan(cursor, qr_input, request)

                # Try Commercial Invoice via GRDETAILS
                cursor.execute("""
                    SELECT CI.CODE
                    FROM DB2INST1.COMMERCIALINVOICE CI
                    LEFT JOIN DB2INST1.SKPCOMMERCIALINVOICE DC
                        ON DC.COMPANYCODE = CI.COMPANYCODE
                        AND DC.DIVISIONCODE = CI.DIVISIONCODE
                        AND DC.CODE = CI.CODE
                    WHERE CI.COMPANYCODE = '100'
                      AND DC.GRDETAILS = %s
                """, [qr_input])
                commercial_invoice_row = cursor.fetchone()

                if commercial_invoice_row:
                    commercial_invoice_code = commercial_invoice_row[0]
                    return handle_commercial_invoice_by_code(cursor, commercial_invoice_code, request)

                # Try Plant Invoice by CHALLANNO
                cursor.execute("""
                    SELECT PL.CODE
                    FROM DB2INST1.PLANTINVOICE PL
                    WHERE PL.COMPANYCODE = '100'
                      AND PL.CHALLANNO = %s
                """, [qr_input])
                plant_invoice_row = cursor.fetchone()

                if plant_invoice_row:
                    plant_invoice_code = plant_invoice_row[0]
                    return handle_plant_invoice_by_code(cursor, plant_invoice_code, request)

                # Check if it's a Commercial Invoice by CHALLANNO
                cursor.execute("""
                    SELECT CODE FROM DB2INST1.COMMERCIALINVOICE 
                    WHERE CHALLANNO = %s
                    FETCH FIRST 1 ROWS ONLY
                """, [qr_input])
                commercial_invoice_row = cursor.fetchone()

                if commercial_invoice_row:
                    commercial_invoice_code = commercial_invoice_row[0]
                    return handle_commercial_invoice_by_code(cursor, commercial_invoice_code, request)

                # Check if it's a Plant Invoice by CHALLANNO
                cursor.execute("""
                    SELECT CODE FROM DB2INST1.PLANTINVOICE 
                    WHERE CHALLANNO = %s
                    FETCH FIRST 1 ROWS ONLY
                """, [qr_input])
                plant_invoice_row = cursor.fetchone()

                if plant_invoice_row:
                    plant_invoice_code = plant_invoice_row[0]
                    return handle_plant_invoice_by_code(cursor, plant_invoice_code, request)

                error_message = "Details Not Found! Invalid QR Code."

    return render(request, 'pages/scan.html', {
        'trips': trips,
        'error_message': error_message
    })


def handle_commercial_invoice_by_code(cursor, invoice_code, request):
    trips = []
    error_message = None

    cursor.execute("""
        SELECT 
            CI.COMPANYCODE, CI.DIVISIONCODE, CI.INVOICETYPECODE, CI.INVOICEDATE,
            CI.DELIVERYPOINTCODE, CI.CODE,
            CASE 
                WHEN CI.DELIVERYPOINTCODE = '' THEN BD.LEGALNAME1 
                ELSE AD.ADDRESSEE 
            END AS ADDRESS,
            CI.CATEGORY, CI.CONTAINERNO,
            CIL.PACKINGQTY, CIL.PRIMARYUMCODE, CIL.PRIMARYQTY,
            CI.ABSUNIQUEID
        FROM DB2INST1.COMMERCIALINVOICE CI
        LEFT JOIN DB2INST1.SKPCOMMERCIALINVOICE DC
            ON DC.COMPANYCODE = CI.COMPANYCODE AND DC.DIVISIONCODE = CI.DIVISIONCODE AND DC.CODE = CI.CODE
        LEFT JOIN DB2INST1.ADDRESS AD
            ON AD.UNIQUEID = CI.DELIVERYPOINTUNIQUEID AND AD.CODE = CI.DELIVERYPOINTCODE
        LEFT JOIN DB2INST1.ORDERPARTNER OD
            ON OD.CUSTOMERSUPPLIERCOMPANYCODE = CI.COMPANYCODE
            AND OD.CUSTOMERSUPPLIERTYPE = CI.CONSIGNEECUSTOMERSUPPLIERTYPE
            AND OD.CUSTOMERSUPPLIERCODE = CI.CONSIGNEECUSTOMERSUPPLIERCODE
        LEFT JOIN DB2INST1.BUSINESSPARTNER BD
            ON BD.NUMBERID = OD.ORDERBUSINESSPARTNERNUMBERID
        LEFT JOIN DB2INST1.COMMERCIALINVOICELINE CIL
            ON CIL.COMMERCIALINVOICECOMPANYCODE = CI.COMPANYCODE
            AND CIL.COMMERCIALINVOICEDIVISIONCODE = CI.DIVISIONCODE
            AND CIL.COMMERCIALINVOICECODE = CI.CODE
        WHERE CI.CODE = %s
        FETCH FIRST 1 ROWS ONLY
    """, [invoice_code])

    row = cursor.fetchone()

    if row:
        trips.append({
            'companycode': row[0] or '',
            'divisioncode': row[1] or '',
            'invoicetype': row[2] or '',
            'invoicedate': row[3].strftime('%Y-%m-%d') if row[3] else '',
            'deliverypointcode': row[4] or '',
            'documentcode': row[5] or '',
            'addressee': row[6] or '',
            'category': row[7] or '',
            'containerno': row[8] or '',
            'packingqty': row[9] or '',
            'uom': row[10] or '',
            'quantity': row[11] or '',
            'absuniqueid': row[12] or '',
            'document_type': 'COMMERCIAL_INVOICE'
        })
    else:
        error_message = "Invoice data not found for this code!"

    return render(request, 'pages/scan.html', {
        'trips': trips,
        'error_message': error_message
    })


def handle_dc_scan(cursor, qr_input, request):
    trips = []
    error_message = None
    
    # Check if provisional code exists
    cursor.execute("""
        SELECT COUNT(*) FROM DB2INST1.INTERNALDOCUMENT 
        WHERE PROVISIONALCODE = %s
    """, [qr_input])
    code_exists = cursor.fetchone()[0] > 0

    if not code_exists:
        error_message = "Details Not Found!"
    else:
        # Check if already gated out
        cursor.execute("""
            SELECT COUNT(*) FROM DB2INST1.ADSTORAGE
            WHERE UNIQUEID IN (
                SELECT ABSUNIQUEID FROM DB2INST1.INTERNALDOCUMENT
                WHERE PROVISIONALCODE = %s
            )
            AND NAMENAME = 'OUTWARDNO'
            AND FIELDNAME = 'OUTWARDNO'
        """, [qr_input])
        
        already_gated_out = cursor.fetchone()[0] > 0
        
        if already_gated_out:
            # Get outward details to show in the message
            cursor.execute("""
                SELECT VALUESTRING, VALUEDATE
                FROM DB2INST1.ADSTORAGE
                WHERE UNIQUEID IN (
                    SELECT ABSUNIQUEID FROM DB2INST1.INTERNALDOCUMENT
                    WHERE PROVISIONALCODE = %s
                )
                AND NAMENAME = 'OUTWARDNO'
                AND FIELDNAME = 'OUTWARDNO'
            """, [qr_input])
            outward_info = cursor.fetchone()
            
            if outward_info:
                outward_no = outward_info[0] or "N/A"
                outward_date = outward_info[1].strftime('%Y-%m-%d') if outward_info[1] else "N/A"
                error_message = f"This DC has already been gated out! Outward No: {outward_no}"
            else:
                error_message = "This DC has already been gated out!"

        # Fetch trip data
        cursor.execute("""
            SELECT 
                ID.COMPANYCODE,
                ID.DIVISIONCODE,
                ID.PROVISIONALCODE,
                IDL.ITEMDESCRIPTION,
                IDL.BASEPRIMARYQUANTITY,
                IDL.BASEPRIMARYUOMCODE,
                AD.ADDRESSEE,
                ADS_VALUESTRING(ID.ABSUNIQUEID, 'InternalDocument', 'VEHICLENUMBER', 'VEHICLENUMBER'),
                ADS_VALUESTRING(ID.ABSUNIQUEID, 'InternalDocument', 'NoofPackages', 'NoofPackages'),
                ADS_VALUESTRING(ID.ABSUNIQUEID, 'InternalDocument', 'MOBILENO', 'MOBILENO'),
                ADS_VALUESTRING(ID.ABSUNIQUEID, 'InternalDocument', 'DRIVERNAME', 'DRIVERNAME')
            FROM DB2INST1.INTERNALDOCUMENT ID
            LEFT OUTER JOIN DB2INST1.INTERNALDOCUMENTLINE IDL
                ON IDL.INTERNALDOCUMENTCOMPANYCODE = ID.COMPANYCODE
                AND IDL.INTDOCPROVISIONALCOUNTERCODE = ID.PROVISIONALCOUNTERCODE
                AND IDL.INTDOCUMENTPROVISIONALCODE = ID.PROVISIONALCODE
            LEFT OUTER JOIN DB2INST1.ADDRESS AD 
                ON AD.UNIQUEID = ID.DELIVERYPOINTUNIQUEID
                AND AD.CODE = ID.DELIVERYPOINTCODE
            WHERE ID.PROVISIONALCODE = %s
            FETCH FIRST 1 ROWS ONLY
        """, [qr_input])

        row = cursor.fetchone()
        if row:
            trips.append({
                'companycode': row[0] or '',
                'divisioncode': row[1] or '',
                'provisionalcode': row[2] or '',
                'itemdescription': row[3] or '',
                'baseprimaryquantity': row[4] or '',
                'baseprimaryuomcode': row[5] or '',
                'addressee': row[6] or '',
                'vehiclenumber': row[7] or '',
                'noofpackages': extract_int(row[8]),
                'mobileno': row[9] or '',
                'drivername': row[10] or '',
                'document_type': 'DC'
            })

    return render(request, 'pages/scan.html', {
        'trips': trips,
        'error_message': error_message
    })


def handle_plant_invoice_by_code(cursor, invoice_code, request):
    trips = []
    error_message = None

    cursor.execute("""
        SELECT 
            PL.COMPANYCODE, PL.DIVISIONCODE, PL.INVOICETYPECODE, PL.INVOICEDATE, 
            PL.DELIVERYPOINTCODE, PL.CODE, PL.CHALLANNO, PL.CHALLANDATE,
            CASE WHEN PL.DELIVERYPOINTCODE = '' THEN BD.LEGALNAME1 ELSE AD.ADDRESSEE END AS ADDRESS,
            PL.CATEGORY, PL.CONTAINERNO, PLI.PACKINGQTY, PLI.PRIMARYUMCODE, PLI.PRIMARYQTY,
            PL.ABSUNIQUEID
        FROM DB2INST1.PLANTINVOICE PL
        LEFT JOIN DB2INST1.ADDRESS AD
            ON AD.UNIQUEID = PL.DELIVERYPOINTUNIQUEID AND AD.CODE = PL.DELIVERYPOINTCODE
        LEFT JOIN DB2INST1.ORDERPARTNER OD
            ON OD.CUSTOMERSUPPLIERCOMPANYCODE = PL.COMPANYCODE
            AND OD.CUSTOMERSUPPLIERTYPE = PL.CONSIGNEECUSTOMERSUPPLIERTYPE
            AND OD.CUSTOMERSUPPLIERCODE = PL.CONSIGNEECUSTOMERSUPPLIERCODE
        LEFT JOIN DB2INST1.BUSINESSPARTNER BD
            ON BD.NUMBERID = OD.ORDERBUSINESSPARTNERNUMBERID
        LEFT JOIN DB2INST1.PLANTINVOICELINE PLI
            ON PLI.PLANTINVOICECOMPANYCODE = PL.COMPANYCODE
            AND PLI.PLANTINVOICEDIVISIONCODE = PL.DIVISIONCODE
            AND PLI.PLANTINVOICECODE = PL.CODE
        WHERE PL.CODE = %s
        FETCH FIRST 1 ROWS ONLY
    """, [invoice_code])

    row = cursor.fetchone()

    if row:
        trips.append({
            'companycode': row[0] or '',
            'divisioncode': row[1] or '',
            'invoicetype': row[2] or '',
            'invoicedate': row[3].strftime('%Y-%m-%d') if row[3] else '',
            'deliverypointcode': row[4] or '',
            'documentcode': row[5] or '',
            'challanno': row[6] or '',
            'challandate': row[7].strftime('%Y-%m-%d') if row[7] else '',
            'addressee': row[8] or '',
            'category': row[9] or '',
            'containerno': row[10] or '',
            'packingqty': row[11] or '',
            'uom': row[12] or '',
            'quantity': row[13] or '',
            'absuniqueid': row[14] or '',
            'document_type': 'PLANT_INVOICE'
        })
    else:
        error_message = "Plant Invoice data not found for this code!"

    return render(request, 'pages/scan.html', {
        'trips': trips,
        'error_message': error_message
    })


# final working for commercial and plant but not internal

# views.py

def internal_gate_out(request):
    if request.method == 'POST':
        try:
            data = request.POST
            provisional_code = data.get('provisionalcode')
            company_code = data.get('companycode')
            division_code = data.get('divisioncode')

            if not provisional_code:
                return JsonResponse({'status': 'error', 'message': 'Provisional code is required'}, status=400)

            with connection.cursor() as cursor:
                # First check if already gated out
                cursor.execute("""
                    SELECT COUNT(*) FROM DB2INST1.ADSTORAGE
                    WHERE UNIQUEID IN (
                        SELECT ABSUNIQUEID FROM DB2INST1.INTERNALDOCUMENT
                        WHERE PROVISIONALCODE = %s
                    )
                    AND NAMENAME = 'OUTWARDNO'
                    AND FIELDNAME = 'OUTWARDNO'
                """, [provisional_code])
                
                already_gated_out = cursor.fetchone()[0] > 0
                
                if already_gated_out:
                    # Get outward details to return in response
                    cursor.execute("""
                        SELECT VALUESTRING, VALUEDATE
                        FROM DB2INST1.ADSTORAGE
                        WHERE UNIQUEID IN (
                            SELECT ABSUNIQUEID FROM DB2INST1.INTERNALDOCUMENT
                            WHERE PROVISIONALCODE = %s
                        )
                        AND NAMENAME = 'OUTWARDNO'
                        AND FIELDNAME = 'OUTWARDNO'
                    """, [provisional_code])
                    outward_info = cursor.fetchone()
                    
                    if outward_info:
                        return JsonResponse({
                            'status': 'error', 
                            'message': f'This DC has already been gated out! Outward No: {outward_info[0]}, Date: {outward_info[1].strftime("%m-%d-%Y")}',
                            'already_gated_out': True
                        })
                    else:
                        return JsonResponse({
                            'status': 'error', 
                            'message': 'This DC has already been gated out!',
                            'already_gated_out': True
                        })

                # Get ABSUNIQUEID
                cursor.execute("""
                    SELECT ABSUNIQUEID 
                    FROM INTERNALDOCUMENT 
                    WHERE PROVISIONALCODE = %s
                """, [provisional_code])

                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'status': 'error', 'message': 'Provisional code not found'}, status=404)

                absuniqueid = row[0]

                # Generate outward number
                division_map = {
                    'COMP01': '101',
                    'COMP02': '102',
                    'COMP03': '103',
                    'COMP04': '106',
                    'COMP05': '107',
                }
                fixed_part = division_map.get(company_code, '102')

                current_year = datetime.datetime.now().strftime('%y')
                search_pattern = f"{current_year}{fixed_part}%"

                cursor.execute("""
                    SELECT 
                        COALESCE(MAX(CAST(RIGHT(VALUESTRING, 5) AS INTEGER)), 0) AS MAX_NUM
                    FROM ADSTORAGE
                    WHERE NAMENAME = 'OUTWARDNO'
                      AND FIELDNAME = 'OUTWARDNO'
                      AND VALUESTRING LIKE %s
                """, [search_pattern])

                max_num = cursor.fetchone()[0] or 0
                new_num = max_num + 1
                outward_no = f"{current_year}{fixed_part}{str(new_num).zfill(5)}"

                # OUTWARDDATE
                cursor.execute("""
                    SELECT VALUEDATE 
                    FROM ADSTORAGE 
                    WHERE UNIQUEID = %s AND NAMENAME = 'OutwardDate' AND FIELDNAME = 'OutwardDate'
                """, [absuniqueid])
                outward_date_row = cursor.fetchone()

                if outward_date_row:
                    cursor.execute("""
                        UPDATE ADSTORAGE
                        SET VALUEDATE = CURRENT_DATE
                        WHERE UNIQUEID = %s 
                        AND NAMENAME = 'OutwardDate' 
                        AND FIELDNAME = 'OutwardDate'
                    """, [absuniqueid])
                else:
                    cursor.execute("""
                        INSERT INTO ADSTORAGE (
                            UNIQUEID, NAMEENTITYNAME, NAMENAME, FIELDNAME,
                            KEYSEQUENCE, SHARED, DATATYPE, VALUEINT,
                            VALUEBOOLEAN, VALUELONG, ABSUNIQUEID, VALUEDATE
                        ) VALUES (
                            %s, 'InternalDocument', 'OutwardDate', 'OutwardDate',
                            0, 0, 0, 0,
                            0, 0, %s, CURRENT_DATE
                        )
                    """, [absuniqueid, absuniqueid])

                # OUTWARDNO
                cursor.execute("""
                    SELECT *
                    FROM ADSTORAGE
                    WHERE UNIQUEID = %s 
                    AND NAMENAME = 'OUTWARDNO' 
                    AND FIELDNAME = 'OUTWARDNO'
                """, [absuniqueid])
                outward_no_row = cursor.fetchone()

                if outward_no_row:
                    cursor.execute("""
                        UPDATE ADSTORAGE
                        SET VALUESTRING = %s
                        WHERE UNIQUEID = %s
                        AND NAMENAME = 'OUTWARDNO'
                        AND FIELDNAME = 'OUTWARDNO'
                    """, [outward_no, absuniqueid])
                else:
                    cursor.execute("""
                        INSERT INTO ADSTORAGE (
                            UNIQUEID, NAMEENTITYNAME, NAMENAME, FIELDNAME,
                            KEYSEQUENCE, SHARED, DATATYPE, VALUESTRING,
                            VALUEINT, VALUEBOOLEAN, VALUELONG, ABSUNIQUEID
                        ) VALUES (
                            %s, 'InternalDocument', 'OUTWARDNO', 'OUTWARDNO',
                            0, 0, 0, %s,
                            0, 0, 0, %s
                        )
                    """, [absuniqueid, outward_no, absuniqueid])

                # Insert into SKAPSTESTDATA
                # cursor.execute("""
                #     INSERT INTO DB2INST1.SKAPSTESTDATA (
                #         COMPANYCODE, DIVISIONCODE, PROVISIONALCODE,
                #         ITEMDESCRIPTION, QUANTITY, UOM, ADDRESSEE,
                #         VEHICLENUMBER, NOOFPACKAGES, MOBILENO, DRIVERNAME,
                #         GATEOUT_TIMESTAMP, SCAN_TIMESTAMP
                #     ) VALUES (
                #         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                #     )
                # """, [
                #     company_code, division_code, provisional_code,
                #     data.get('itemdescription'), data.get('baseprimaryquantity'),
                #     data.get('baseprimaryuomcode'), data.get('addressee'),
                #     data.get('vehiclenumber'), extract_int(data.get('noofpackages')),
                #     data.get('mobileno'), data.get('drivername')
                # ])

            return JsonResponse({
                'status': 'success',
                'message': 'Gate out processed successfully',
                'outward_no': outward_no  # Removed absuniqueid from response as it's not used in the frontend
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def commercial_plant_gate_out(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            print("Received POST data:", data)

            code_value = data.get('documentcode') or data.get('qr_code_value')
            company_code = data.get('companycode')
            division_code = data.get('divisioncode')
            document_type = data.get('document_type')

            if not code_value:
                return JsonResponse({'status': 'error', 'message': 'Document code is missing'}, status=400)

            with connection.cursor() as cursor:
                # Auto-detect document type if not provided
                if not document_type:
                    cursor.execute("SELECT COUNT(*) FROM DB2INST1.COMMERCIALINVOICE WHERE CODE = %s", [code_value])
                    if cursor.fetchone()[0] > 0:
                        document_type = 'COMMERCIAL_INVOICE'
                    else:
                        cursor.execute("SELECT COUNT(*) FROM DB2INST1.PLANTINVOICE WHERE CODE = %s", [code_value])
                        if cursor.fetchone()[0] > 0:
                            document_type = 'PLANT_INVOICE'
                        else:
                            return JsonResponse({'status': 'error', 'message': 'Document not found'}, status=404)

                # Map table and entity name
                if document_type == 'COMMERCIAL_INVOICE':
                    table_name = 'COMMERCIALINVOICE'
                    code_field = 'CODE'
                    name_entity = 'CommercialInvoice'
                elif document_type == 'PLANT_INVOICE':
                    table_name = 'PLANTINVOICE'
                    code_field = 'CODE'
                    name_entity = 'PlantInvoice'
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid document type'}, status=400)

                # Check if already gated out
                cursor.execute(f"""
                    SELECT COUNT(*) FROM DB2INST1.ADSTORAGE
                    WHERE UNIQUEID IN (
                        SELECT ABSUNIQUEID FROM DB2INST1.{table_name}
                        WHERE {code_field} = %s
                    )
                    AND NAMENAME = 'OutwardNo' AND FIELDNAME = 'OutwardNo'
                """, [code_value])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'status': 'error', 'message': 'Already gated out'})

                # Get ABSUNIQUEID
                cursor.execute(f"""
                    SELECT ABSUNIQUEID FROM DB2INST1.{table_name}
                    WHERE {code_field} = %s
                """, [code_value])
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'status': 'error', 'message': 'Document not found'}, status=404)
                absuniqueid = row[0]

                # Generate OutwardNo
                division_map = {
                    'COMP01': '101', 'COMP02': '102',
                    'COMP03': '103', 'COMP04': '106',
                    'COMP05': '107'
                }
                fixed_part = division_map.get(company_code, '101')
                current_year = datetime.datetime.now().strftime('%y')
                search_pattern = f"{current_year}{fixed_part}%"

                cursor.execute("""
                    SELECT COALESCE(MAX(CAST(RIGHT(VALUESTRING, 5) AS INTEGER)), 0)
                    FROM DB2INST1.ADSTORAGE
                    WHERE NAMENAME = 'OutwardNo' AND FIELDNAME = 'OutwardNo'
                    AND VALUESTRING LIKE %s
                """, [search_pattern])
                max_no = cursor.fetchone()[0] or 0
                outward_no = f"{current_year}{fixed_part}{str(max_no + 1).zfill(5)}"

                # Insert or update OutwardDate
                cursor.execute("""
                    SELECT COUNT(*) FROM DB2INST1.ADSTORAGE
                    WHERE UNIQUEID = %s AND NAMENAME = 'OutwardDate' AND FIELDNAME = 'OutwardDate'
                """, [absuniqueid])
                if cursor.fetchone()[0] > 0:
                    cursor.execute("""
                        UPDATE DB2INST1.ADSTORAGE
                        SET VALUEDATE = CURRENT_DATE
                        WHERE UNIQUEID = %s AND NAMENAME = 'OutwardDate' AND FIELDNAME = 'OutwardDate'
                    """, [absuniqueid])
                else:
                    cursor.execute("""
                        INSERT INTO DB2INST1.ADSTORAGE (
                            UNIQUEID, NAMEENTITYNAME, NAMENAME, FIELDNAME,
                            KEYSEQUENCE, SHARED, DATATYPE, VALUEINT,
                            VALUEBOOLEAN, VALUELONG, ABSUNIQUEID, VALUEDATE
                        ) VALUES (
                            %s, %s, 'OutwardDate', 'OutwardDate',
                            0, 0, 0, 0,
                            0, 0, %s, CURRENT_DATE
                        )
                    """, [absuniqueid, name_entity, absuniqueid])

                # Insert or update OutwardNo
                cursor.execute("""
                    SELECT COUNT(*) FROM DB2INST1.ADSTORAGE
                    WHERE UNIQUEID = %s AND NAMENAME = 'OutwardNo' AND FIELDNAME = 'OutwardNo'
                """, [absuniqueid])
                if cursor.fetchone()[0] > 0:
                    cursor.execute("""
                        UPDATE DB2INST1.ADSTORAGE
                        SET VALUESTRING = %s
                        WHERE UNIQUEID = %s AND NAMENAME = 'OutwardNo' AND FIELDNAME = 'OutwardNo'
                    """, [outward_no, absuniqueid])
                else:
                    cursor.execute("""
                        INSERT INTO DB2INST1.ADSTORAGE (
                            UNIQUEID, NAMEENTITYNAME, NAMENAME, FIELDNAME,
                            KEYSEQUENCE, SHARED, DATATYPE, VALUESTRING,
                            VALUEINT, VALUEBOOLEAN, VALUELONG, ABSUNIQUEID
                        ) VALUES (
                            %s, %s, 'OutwardNo', 'OutwardNo',
                            0, 0, 0, %s,
                            0, 0, 0, %s
                        )
                    """, [absuniqueid, name_entity, outward_no, absuniqueid])

                return JsonResponse({
                    'status': 'success', 
                    'message': 'Gate out successful', 
                    'outward_no': outward_no
                })

        except Exception as e:
            print("Gate out error:", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)