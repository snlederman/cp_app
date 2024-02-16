from django.http import JsonResponse
from .utils import process_csv
from django.views.decorators.csrf import csrf_exempt
import cProfile
import pstats
import io
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'File is not CSV type'}, status=400)

        # Start profiling
        pr = cProfile.Profile()
        pr.enable()

        # Directly pass the file stream to process_csv
        response_data = process_csv(csv_file)

        pr.disable()

        # Create a stream to capture profiling data
        s = io.StringIO()
        sortby = 'cumulative'

        # Create a Stats object based on the stream and sort the results
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)

        # Print the stats to the stream
        ps.print_stats()

        # Get the profiling data from the stream
        profiling_data = s.getvalue()

        # Do something with the profiling data (print it, log it, etc.)
        print(profiling_data)

        return JsonResponse({'data': response_data}, safe=False)
    else:
        return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)
