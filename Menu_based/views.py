from django.shortcuts import render
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Category,FAQ
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging

def chatbot(request):
    return render(request, 'FrontEnd/chatbot.html')


# data import form json file and save in data base 
def import_faq_data(request):
    json_file_path = r'E:\Chatbot\Chatbot\Menu_based\FypDatase.json'  # Use a raw string to avoid escape issues

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        def create_category(category_id, category_info, parent=None):
            # Create or update the category
            category, _ = Category.objects.update_or_create(
                category_number=category_id,
                defaults={
                    'name': category_info.get('name'),
                    'parent_category': parent
                }
            )

            # Check if an answer is present in the current category
            if 'answer' in category_info:
                FAQ.objects.update_or_create(
                    category=category,
                    question_text=category_info.get('name'),
                    defaults={
                        'answer_text': category_info.get('answer')
                    }
                )

            # Recursively process children
            for sub_id, sub_info in category_info.get('children', {}).items():
                if isinstance(sub_info, dict):
                    create_category(sub_id, sub_info, parent=category)

        # Start processing from the top-level categories
        for category_id, category_info in data.items():
            create_category(category_id, category_info)

        return HttpResponse("FAQ data imported successfully!")

    except Exception as e:
        return HttpResponse(f"Error importing FAQ data: {e}")
    

# This function fetches the menu options

logger = logging.getLogger(__name__)

def get_menu_options(request):
    # Fetch only main categories (no parent)
    try:
        main_categories = Category.objects.filter(parent_category__isnull=True)
        menu_options = [
            {
                'category_number': index + 1,
                'name': category.name,
            }
            for index, category in enumerate(main_categories)
        ]
        return JsonResponse(menu_options, safe=False)
    except Exception as e:
        logger.error(f"Error fetching menu options: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def process_input(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('userInput', '')

            # Fetch main categories
            main_categories = list(Category.objects.filter(parent_category__isnull=True))

            if user_input.isdigit():
                selected_index = int(user_input) - 1
                if 0 <= selected_index < len(main_categories):
                    selected_category = main_categories[selected_index]
                    subcategories = selected_category.subcategories.all()
                    response = {
                        "message": f"You selected {selected_category.name}.",
                        "subcategories": [{"name": sub.name} for sub in subcategories],
                    }
                    return JsonResponse(response)

            return JsonResponse({"message": "Invalid input. Please select a valid category."})

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format."}, status=400)
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=400)

#function for subcategory processing
logger = logging.getLogger(__name__)

@csrf_exempt
def process_subcategory_input(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            main_category_index = data.get('mainCategoryIndex', None)
            subcategory_input = data.get('subcategoryInput', '')
            current_category_path = data.get('currentCategoryPath', [])

            # Validate input
            if main_category_index is None or not isinstance(main_category_index, int):
                return JsonResponse({"message": "Invalid main category index."}, status=400)

            # Fetch main categories
            main_categories = list(Category.objects.filter(parent_category__isnull=True))

            response = {
                "message": "Invalid subcategory option. Please try again."
            }

            if 0 <= main_category_index < len(main_categories):
                selected_category = main_categories[main_category_index]

                # Traverse the current category path
                for path_item in current_category_path:
                    if 'subcategoryInput' in path_item:
                        subcategories = selected_category.subcategories.all()
                        if 0 <= int(path_item['subcategoryInput']) - 1 < len(subcategories):
                            selected_category = subcategories[int(path_item['subcategoryInput']) - 1]

                # At the selected category level
                subcategories = selected_category.subcategories.all()

                if not subcategories:
                    # No further subcategories, fetch answer from FAQ
                    faq = FAQ.objects.filter(category=selected_category).first()
                    response['message'] = f"You selected subcategory '{selected_category.name}'."
                    response['details'] = faq.answer_text if faq else "No answer found."
                else:
                    # There are subcategories, process further
                    if subcategory_input.isdigit():
                        selected_sub_index = int(subcategory_input) - 1
                        if 0 <= selected_sub_index < len(subcategories):
                            selected_subcategory = subcategories[selected_sub_index]
                            subchildren = selected_subcategory.subcategories.all()

                            if subchildren.exists():
                                subchildren_list = [
                                    {"index": index + 1, "name": child.name} for index, child in enumerate(subchildren)
                                ]
                                response['message'] = f"Subcategory '{selected_subcategory.name}' has the following options:"
                                response['subchildren'] = subchildren_list
                            else:
                                # If no subchildren, return the FAQ answer
                                faq = FAQ.objects.filter(category=selected_subcategory).first()
                                if faq:
                                    response['message'] = f"You selected subcategory '{selected_subcategory.name}'."
                                    response['details'] = faq.answer_text
                                else:
                                    response['message'] = f"You selected subcategory '{selected_subcategory.name}', but no answer found."
                                    response['details'] = "No answer found."

                            return JsonResponse(response)

            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format."}, status=400)
        except Exception as e:
            logger.error(f"Error processing subcategory input: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=400)


