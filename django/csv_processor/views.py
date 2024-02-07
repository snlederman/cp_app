from django.http import JsonResponse
from .utils import process_csv
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'File is not CSV type'}, status=400)

        # Directly pass the file stream to process_csv
        response_data = process_csv(csv_file)
        return JsonResponse({'data': response_data}, safe=False)
    else:
        return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)
