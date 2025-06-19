# from django.shortcuts import render
# from django.db import connection
# from django.http import JsonResponse
# import datetime

# def scanner(request):
#     trips = []

#     if request.method == 'POST':
#         qr_input = request.POST.get('qr_code_value')
        
#         if qr_input:
#             with connection.cursor() as cursor:
#                 # Check if SKAPSTESTDATA table exists, if not create it
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM SYSIBM.SYSTABLES 
#                     WHERE CREATOR = 'DB2INST1' AND NAME = 'SKAPSTESTDATA'
#                 """)
#                 table_exists = cursor.fetchone()[0] > 0
                
#                 if not table_exists:
#                     cursor.execute("""
#                         CREATE TABLE DB2INST1.SKAPSTESTDATA (
#                             ID INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
#                             COMPANYCODE VARCHAR(10),
#                             DIVISIONCODE VARCHAR(10),
#                             PROVISIONALCODE VARCHAR(20),
#                             ITEMDESCRIPTION VARCHAR(100),
#                             QUANTITY DECIMAL(10,2),
#                             UOM VARCHAR(10),
#                             ADDRESSEE VARCHAR(100),
#                             VEHICLENUMBER VARCHAR(20),
#                             NOOFPACKAGES INTEGER,
#                             MOBILENO VARCHAR(15),
#                             DRIVERNAME VARCHAR(50),
#                             GATEOUT_TIMESTAMP TIMESTAMP,
#                             SCAN_TIMESTAMP TIMESTAMP
#                         )
#                     """)
                
#                 # Fetch the trip data
#                 cursor.execute("""
#                     SELECT 
#                         ID.COMPANYCODE,
#                         ID.DIVISIONCODE,
#                         ID.PROVISIONALCODE,
#                         IDL.ITEMDESCRIPTION,
#                         IDL.BASEPRIMARYQUANTITY,
#                         IDL.BASEPRIMARYUOMCODE,
#                         AD.ADDRESSEE,
#                         ADS_VALUESTRING(ID.ABSUNIQUEID, 'InternalDocument', 'VEHICLENUMBER', 'VEHICLENUMBER') AS VehicleNumber,
#                         ADS_VALUESTRING(ID.ABSUNIQUEID, 'InternalDocument', 'NoofPackages', 'NoofPackages') AS NoOfPackages,
#                         ADS_VALUESTRING(ID.ABSUNIQUEID, 'InternalDocument', 'MOBILENO', 'MOBILENO') AS MobileNo,
#                         ADS_VALUESTRING(ID.ABSUNIQUEID, 'InternalDocument', 'DRIVERNAME', 'DRIVERNAME') AS DriverName
#                     FROM DB2INST1.INTERNALDOCUMENT ID
#                     LEFT OUTER JOIN DB2INST1.INTERNALDOCUMENTLINE IDL
#                         ON IDL.INTERNALDOCUMENTCOMPANYCODE = ID.COMPANYCODE
#                         AND IDL.INTDOCPROVISIONALCOUNTERCODE = ID.PROVISIONALCOUNTERCODE
#                         AND IDL.INTDOCUMENTPROVISIONALCODE = ID.PROVISIONALCODE
#                     LEFT OUTER JOIN DB2INST1.ADDRESS AD 
#                         ON AD.UNIQUEID = ID.DELIVERYPOINTUNIQUEID
#                         AND AD.CODE = ID.DELIVERYPOINTCODE
#                     WHERE ID.PROVISIONALCODE = %s
#                     FETCH FIRST 1 ROWS ONLY
#                 """, [qr_input])

#                 row = cursor.fetchone()
#                 if row:
#                     trips.append({
#                         # 'companycode': row[0] or '',
#                         # 'divisioncode': row[1] or '',
#                         'provisionalcode': row[2] or '',
#                         'itemdescription': row[3] or '',
#                         'baseprimaryquantity': row[4] or '',
#                         # 'baseprimaryuomcode': row[5] or '',
#                         'addressee': row[6] or '',
#                         'vehiclenumber': row[7] or '',
#                         'noofpackages': row[8] or '',
#                         'mobileno': row[9] or '',
#                         'drivername': row[10] or '',
#                     })

#     return render(request, 'pages/scan.html', {'trips': trips})

# # def gate_out(request):
# #     if request.method == 'POST':
# #         try:
# #             data = request.POST
# #             current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
# #             # Ensure numeric types are converted properly
# #             try:
# #                 quantity = float(data.get('quantity')) if data.get('quantity') else 0.0
# #             except ValueError:
# #                 quantity = 0.0

# #             try:
# #                 noofpackages = int(data.get('noofpackages')) if data.get('noofpackages') else 0
# #             except ValueError:
# #                 noofpackages = 0

# #             with connection.cursor() as cursor:
# #                 # Add debug logs before insert
# #                 print("QUANTITY:", quantity)
# #                 print("NOOFPACKAGES:", noofpackages)

# #                 cursor.execute("""
# #                     INSERT INTO DB2INST1.SKAPSTESTDATA (
# #                         PROVISIONALCODE, QUANTITY, UOM, 
# #                         ADDRESSEE, VEHICLENUMBER, NOOFPACKAGES, 
# #                         MOBILENO, DRIVERNAME, GATEOUT_TIMESTAMP, SCAN_TIMESTAMP
# #                     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
# #                 """, [
# #                     data.get('provisionalcode'),
# #                     quantity,
# #                     data.get('uom'),
# #                     data.get('addressee'),
# #                     data.get('vehiclenumber'),
# #                     noofpackages,
# #                     data.get('mobileno'),
# #                     data.get('drivername'),
# #                     current_time,
# #                     current_time
# #                 ])

                
# #             return JsonResponse({'status': 'success', 'message': 'Gate out recorded successfully'})
            
# #         except Exception as e:
# #             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# #     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# #  final gate_out
# def gate_out(request):
#     if request.method == 'POST':
#         try:
#             data = request.POST
#             provisional_code = data.get('provisionalcode')
            
#             if not provisional_code:
#                 return JsonResponse({'status': 'error', 'message': 'Provisional code is required'}, status=400)

#             with connection.cursor() as cursor:
#                 # Step 1: Get ABSUNIQUEID from INTERNALDOCUMENT
#                 cursor.execute("""
#                     SELECT ABSUNIQUEID 
#                     FROM INTERNALDOCUMENT 
#                     WHERE PROVISIONALCODE = %s
#                 """, [provisional_code])
                
#                 row = cursor.fetchone()
#                 if not row:
#                     return JsonResponse({'status': 'error', 'message': 'Provisional code not found'}, status=404)
                    
#                 absuniqueid = row[0]
                
#                 # Step 2: Check existing ADSTORAGE entries
#                 cursor.execute("""
#                     SELECT * 
#                     FROM ADSTORAGE 
#                     WHERE UNIQUEID = %s
#                 """, [absuniqueid])
#                 existing_entries = cursor.fetchall()
                
#                 # Step 3: Get max OUTWARDNO
#                 cursor.execute("""
#                     SELECT 
#                         COALESCE(MAX(CAST(VALUESTRING AS INTEGER)), 0) AS MAX_OUTWARDNO
#                     FROM ADSTORAGE
#                     WHERE NAMENAME = 'OUTWARDNO' AND FIELDNAME = 'OUTWARDNO'
#                 """)
#                 max_outward_no = cursor.fetchone()[0] or 0
#                 new_outward_no = max_outward_no + 1
                
#                 # Step 4: Check OUTWARDDATE value
#                 cursor.execute("""
#                     SELECT VALUEDATE 
#                     FROM ADSTORAGE 
#                     WHERE UNIQUEID = %s AND NAMENAME = 'OUTWARDDATE' AND FIELDNAME = 'OUTWARDDATE'
#                 """, [absuniqueid])
#                 outward_date_row = cursor.fetchone()
                
#                 # Step 5: Update or insert OUTWARDDATE
#                 if outward_date_row:
#                     cursor.execute("""
#                         UPDATE ADSTORAGE
#                         SET VALUEDATE = CURRENT_DATE
#                         WHERE UNIQUEID = %s 
#                         AND NAMENAME = 'OUTWARDDATE' 
#                         AND FIELDNAME = 'OUTWARDDATE'
#                     """, [absuniqueid])
#                 else:
#                     cursor.execute("""
#                         INSERT INTO ADSTORAGE (
#                             UNIQUEID, 
#                             NAMEENTITYNAME,
#                             NAMENAME, 
#                             FIELDNAME, 
#                             KEYSEQUENCE, 
#                             SHARED, 
#                             DATATYPE, 
#                             VALUEINT, 
#                             VALUEBOOLEAN, 
#                             VALUELONG, 
#                             ABSUNIQUEID,
#                             VALUEDATE
#                         ) VALUES (
#                             %s, 
#                             'InternalDocument',
#                             'OUTWARDDATE', 
#                             'OUTWARDDATE', 
#                             0, 
#                             0, 
#                             0, 
#                             0, 
#                             0, 
#                             0, 
#                             %s,
#                             CURRENT_DATE
#                         )
#                     """, [absuniqueid, absuniqueid])
                
#                 # Check if OUTWARDNO exists
#                 cursor.execute("""
#                     SELECT *
#                     FROM ADSTORAGE
#                     WHERE UNIQUEID = %s 
#                     AND NAMENAME = 'OUTWARDNO' 
#                     AND FIELDNAME = 'OUTWARDNO'
#                 """, [absuniqueid])
#                 outward_no_row = cursor.fetchone()
                
#                 if outward_no_row:
#                     # Update existing OUTWARDNO
#                     cursor.execute("""
#                         UPDATE ADSTORAGE
#                         SET VALUESTRING = %s
#                         WHERE UNIQUEID = %s
#                         AND NAMENAME = 'OUTWARDNO'
#                         AND FIELDNAME = 'OUTWARDNO'
#                     """, [str(new_outward_no), absuniqueid])
#                 else:
#                     # Insert new OUTWARDNO
#                     cursor.execute("""
#                         INSERT INTO ADSTORAGE (
#                             UNIQUEID, 
#                             NAMEENTITYNAME,
#                             NAMENAME, 
#                             FIELDNAME, 
#                             KEYSEQUENCE, 
#                             SHARED, 
#                             DATATYPE, 
#                             VALUESTRING, 
#                             VALUEINT, 
#                             VALUEBOOLEAN, 
#                             VALUELONG, 
#                             ABSUNIQUEID
#                         ) VALUES (
#                             %s, 
#                             'InternalDocument',
#                             'OUTWARDNO', 
#                             'OUTWARDNO', 
#                             0, 
#                             0, 
#                             0, 
#                             %s, 
#                             0, 
#                             0, 
#                             0, 
#                             %s
#                         )
#                     """, [absuniqueid, str(new_outward_no), absuniqueid])
                
#             return JsonResponse({
#                 'status': 'success', 
#                 'message': 'Gate out processed successfully',
#                 'absuniqueid': absuniqueid,
#                 'outward_no': new_outward_no
#             })
            
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)







# error handing code final version
from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
import datetime
import re

# Helper to safely extract integer from string
def extract_int(value):
    if value is None:
        return 0
    match = re.search(r'\d+', str(value))
    if match:
        return int(match.group())
    return 0

def scanner(request):
    trips = []
    error_message = None

    if request.method == 'POST':
        qr_input = request.POST.get('qr_code_value')

        if qr_input:
            with connection.cursor() as cursor:
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
                        })

    return render(request, 'pages/scan.html', {
        'trips': trips,
        'error_message': error_message
    })

def gate_out(request):
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
                            'message': f'This DC has already been gated out! Outward No: {outward_info[0]}, Date: {outward_info[1].strftime("%Y-%m-%d")}',
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
                    WHERE UNIQUEID = %s AND NAMENAME = 'OUTWARDDATE' AND FIELDNAME = 'OUTWARDDATE'
                """, [absuniqueid])
                outward_date_row = cursor.fetchone()

                if outward_date_row:
                    cursor.execute("""
                        UPDATE ADSTORAGE
                        SET VALUEDATE = CURRENT_DATE
                        WHERE UNIQUEID = %s 
                        AND NAMENAME = 'OUTWARDDATE' 
                        AND FIELDNAME = 'OUTWARDDATE'
                    """, [absuniqueid])
                else:
                    cursor.execute("""
                        INSERT INTO ADSTORAGE (
                            UNIQUEID, NAMEENTITYNAME, NAMENAME, FIELDNAME,
                            KEYSEQUENCE, SHARED, DATATYPE, VALUEINT,
                            VALUEBOOLEAN, VALUELONG, ABSUNIQUEID, VALUEDATE
                        ) VALUES (
                            %s, 'InternalDocument', 'OUTWARDDATE', 'OUTWARDDATE',
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
                cursor.execute("""
                    INSERT INTO DB2INST1.SKAPSTESTDATA (
                        COMPANYCODE, DIVISIONCODE, PROVISIONALCODE,
                        ITEMDESCRIPTION, QUANTITY, UOM, ADDRESSEE,
                        VEHICLENUMBER, NOOFPACKAGES, MOBILENO, DRIVERNAME,
                        GATEOUT_TIMESTAMP, SCAN_TIMESTAMP
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """, [
                    company_code, division_code, provisional_code,
                    data.get('itemdescription'), data.get('baseprimaryquantity'),
                    data.get('baseprimaryuomcode'), data.get('addressee'),
                    data.get('vehiclenumber'), extract_int(data.get('noofpackages')),
                    data.get('mobileno'), data.get('drivername')
                ])

            return JsonResponse({
                'status': 'success',
                'message': 'Gate out processed successfully',
                'absuniqueid': absuniqueid,
                'outward_no': outward_no
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)