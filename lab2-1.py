import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def factorial(n): 
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def binomial_coefficient(n, k): 
    return factorial(n) // (factorial(k) * factorial(n - k))

def theoretical_binomial_probabilities_manual(n, p): 
    probabilities = []
    for k in range(n + 1):
        prob = binomial_coefficient(n, k) * (p ** k) * ((1 - p) ** (n - k))
        probabilities.append(prob)
    return probabilities

def calculate_statistics_manual(data, n, p): 
    expected_value = n * p
    variance = n * p * (1 - p)

    sample_sum = sum(data)
    sample_mean = sample_sum / len(data)
    sample_variance = sum((x - sample_mean) ** 2 for x in data) / len(data)
    sample_median = (sorted(data)[len(data) // 2 - 1] + sorted(data)[len(data) // 2]) / 2 if len(data) % 2 == 0 else sorted(data)[len(data) // 2]
    sample_range = max(data) - min(data)

    return {
        "Eη": expected_value,  
        "Dη": variance,        
        "x̄": sample_mean,      
        "S^2": sample_variance,
        "Me": sample_median,    
        "R": sample_range,      
    }

def plot_distribution_functions_manual(data, theoretical_probs, n): 
    theoretical_cdf = []
    cumulative = 0
    for prob in theoretical_probs:
        cumulative += prob
        theoretical_cdf.append(cumulative)

    sorted_data = sorted(data)
    sample_cdf = []
    for value in range(n + 1):
        count = sum(1 for x in sorted_data if x <= value)
        sample_cdf.append(count / len(data))

    # Вычисление меры расхождения
    max_diff = 0
    xn = 0
    for i in range(n + 1):
        if (theoretical_cdf[i] - sample_cdf[i]) > max_diff:
            max_diff = (theoretical_cdf[i] - sample_cdf[i])
            xn = i
    figure = plt.Figure(figsize=(6, 4), dpi=100)
    ax = figure.add_subplot(111)
    ax.step(range(n + 1), theoretical_cdf, label="Теоретическая Fη(x)", where="post")
    ax.step(range(n + 1), sample_cdf, label="Выборочная F̂η(x)", where="post", linestyle="--")
    ax.set_xlabel("x")
    ax.set_ylabel("F(x)")
    ax.legend()
    ax.set_title("Функции распределения")
    ax.grid()
    return figure,max_diff,xn

# Функция для обновления текста меры расхождения
def update_divergence_label(max_diff, xn):
    divergence_label.config(text=f"Мера расхождения D: {max_diff:.4f} при x={xn}")

def display_frequencies(mas_ni, mas_n, theoretical_probs, n, max_diff, xm):
    # Проверяем, существует ли уже таблица частот
    global stats_tree_2
    if 'stats_tree_2' not in globals():
        freq_frame = ttk.Frame(table_frame)
        freq_frame.pack(side=tk.LEFT, fill='both', expand=True)
        
        ttk.Label(freq_frame, text="Частоты и отклонения", font=("Helvetica", 12, "bold")).pack()

        stats_tree_2 = ttk.Treeview(freq_frame, columns=('y_i', 'P_eta_y_i', 'n_i', 'n_i_n', 'abs_diff'),
                                     show='headings', height=15)
        stats_tree_2.heading('y_i', text='y_i', anchor='w')
        stats_tree_2.heading('P_eta_y_i', text='P(η=y_i)', anchor='w')
        stats_tree_2.heading('n_i', text='n_i', anchor='w')
        stats_tree_2.heading('n_i_n', text='n_i/n', anchor='w')
        stats_tree_2.heading('abs_diff', text='|n_i/n - P|', anchor='w')

        stats_tree_2.column('y_i', anchor='w', width=50)
        stats_tree_2.column('P_eta_y_i', anchor='w', width=100)
        stats_tree_2.column('n_i', anchor='w', width=80)
        stats_tree_2.column('n_i_n', anchor='w', width=80)
        stats_tree_2.column('abs_diff', anchor='w', width=100)

        stats_tree_2.pack(fill='both', expand=True)

        global divergence_label_2
        divergence_label_2 = ttk.Label(freq_frame, text="", font=("Helvetica", 10), justify="center")
        divergence_label_2.pack(pady=5)

    # Очищаем существующую таблицу
    stats_tree_2.delete(*stats_tree_2.get_children())

    # Заполняем таблицу новыми данными
    for i in range(n + 1):
        relative_freq = mas_n[i]
        abs_diff = abs(relative_freq - theoretical_probs[i])
        stats_tree_2.insert('', 'end', values=(
            i, f"{theoretical_probs[i]:.4f}", mas_ni[i], f"{relative_freq:.4f}", f"{abs_diff:.4f}"
        ))

    # Обновляем текст меры расхождения
    divergence_label_2.config(text=f"Мера расхождения D: {max_diff:.4f} при x = {xm}")


def run_experiment():
    try:
        n = int(entry_n.get())
        p = float(entry_p.get())
        experiments = int(entry_experiments.get())

        if n <= 0 or not (0 <= p <= 1) or experiments <= 0:
            raise ValueError("Некорректные данные")

        mas_ni = [0] * (n + 1)
        mas_n = [0] * (n + 1)
        data = []

        for _ in range(experiments):
            distorted_count = 0
            for _ in range(n): 
                if random.random() < p:
                    distorted_count += 1 
            mas_ni[distorted_count] += 1 
            data.append(distorted_count)

        for i in range(len(mas_ni)): 
            mas_n[i] = mas_ni[i] / experiments 

        for i in tree.get_children():
            tree.delete(i)

        for i in range(len(mas_ni)):
            tree.insert('', 'end', values=(f"{i}", mas_ni[i], f"{mas_n[i]:.4f}"))

        theoretical_probs = theoretical_binomial_probabilities_manual(n, p)
        figure, max_diff, xn = plot_distribution_functions_manual(data, theoretical_probs, n)

        statistics = calculate_statistics_manual(data, n, p)

        # Update statistics table
        stats_tree.delete(*stats_tree.get_children())
        stats_tree.insert('', 'end', values=('Eη (мат. ожидание)', f"{statistics['Eη']:.4f}"))
        stats_tree.insert('', 'end', values=('x̄ (среднее)', f"{statistics['x̄']:.4f}"))
        stats_tree.insert('', 'end', values=('Eη - x̄ ', f"{abs(statistics['Eη'] - statistics['x̄']):.4f}"))
        stats_tree.insert('', 'end', values=('Dη (дисперсия)', f"{statistics['Dη']:.4f}"))
        stats_tree.insert('', 'end', values=('S^2 (выборочная дисперсия)', f"{statistics['S^2']:.4f}"))
        stats_tree.insert('', 'end', values=('Dη - S^2', f"{abs(statistics['Dη'] - statistics['S^2']):.4f}"))
        stats_tree.insert('', 'end', values=('Me (медиана)', f"{statistics['Me']:.4f}"))
        stats_tree.insert('', 'end', values=('R (размах)', f"{statistics['R']:.4f}"))

        update_divergence_label(max_diff, xn)

        # Update frequencies and deviations table
        display_frequencies(mas_ni, mas_n, theoretical_probs, n, max_diff, xn)

        # Display graph
        for widget in plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(figure, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    except ValueError:
        messagebox.showerror("Ошибка ввода", "Проверьте введённые значения:\n"
                                             "Число сообщений должно быть > 0,\n"
                                             "Вероятность искажения должна быть в пределах [0, 1],\n"
                                             "Число экспериментов должно быть > 0.")


root = tk.Tk()
root.title("Experiment Results: Channel Distortions")
root.geometry("1000x600")

style = ttk.Style()
style.configure('Treeview', font=('Helvetica', 14))  # Увеличение шрифта
style.configure('Treeview.Heading', font=('Helvetica', 16, 'bold'))  # Увеличение шрифта заголовков

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill='both', expand=True)

param_frame = ttk.LabelFrame(main_frame, text="Параметры эксперимента", padding=10)
param_frame.pack(fill='x', pady=10)

ttk.Label(param_frame, text='Число сообщений n:', font=('Helvetica', 14)).grid(row=0, column=0, sticky='w', pady=5)
entry_n = ttk.Entry(param_frame, font=('Helvetica', 14))
entry_n.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

ttk.Label(param_frame, text='Вероятность искажения p:', font=('Helvetica', 14)).grid(row=1, column=0, sticky='w', pady=5)
entry_p = ttk.Entry(param_frame, font=('Helvetica', 14))
entry_p.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

ttk.Label(param_frame, text='Число экспериментов:', font=('Helvetica', 14)).grid(row=2, column=0, sticky='w', pady=5)
entry_experiments = ttk.Entry(param_frame, font=('Helvetica', 14))
entry_experiments.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

param_frame.columnconfigure(1, weight=1)
# Создаём стиль для увеличения размера текста кнопки
style = ttk.Style()
style.configure("LargeButton.TButton", font=("Arial", 16))  # Увеличиваем шрифт

# Кнопка с увеличенным шрифтом
btn_run = ttk.Button(param_frame, text="Начать вычисления", command=run_experiment, style="LargeButton.TButton")
btn_run.grid(row=3, column=0, columnspan=2, pady=10)

results_frame = ttk.Frame(main_frame, padding=10)
results_frame.pack(fill='both', expand=True)

table_frame = ttk.Frame(results_frame)
table_frame.pack(side=tk.LEFT, fill='both', expand=True)

plot_frame = ttk.Frame(results_frame)
plot_frame.pack(side=tk.RIGHT, fill='both', expand=True)

tree = ttk.Treeview(table_frame, columns=('Value', 'Occurrences', 'Frequency'), show='headings', height=15)
tree.heading('Value', text='Значения с.в.')
tree.heading('Occurrences', text='Число выпадений')
tree.heading('Frequency', text='Частота')
tree.column('Value', anchor='center', width=100)
tree.column('Occurrences', anchor='center', width=150)
tree.column('Frequency', anchor='center', width=150)
tree.pack(fill='both', expand=True)

stats_tree = ttk.Treeview(table_frame, columns=('Parameter', 'Value'), show='headings', height=8)
stats_tree.heading('Parameter', text='Параметр', anchor='w')  # Выравнивание по левому краю
stats_tree.heading('Value', text='Значение', anchor='w')  # Выравнивание по левому краю
stats_tree.column('Parameter', anchor='w', width=150)  # Выравнивание значений
stats_tree.column('Value', anchor='w', width=150)  # Выравнивание значений
stats_tree.pack(fill='both', expand=True)

# Добавляем метку для отображения меры расхождения
divergence_label = ttk.Label(results_frame, text="", font=("Arial", 14), justify="center")
divergence_label.pack(pady=10)

root.mainloop()




# import tkinter as tk
# from tkinter import ttk, messagebox
# import random
# import matplotlib.pyplot as plt

# def factorial(n): #вычисления биномиального коэффициента
# if n == 0 or n == 1:
#     return 1
# result = 1
# for i in range(2, n + 1):
#     result *= i
# return result

# def binomial_coefficient(n, k): #Вычисление числа сочетаний
# return factorial(n) // (factorial(k) * factorial(n - k))

# def theoretical_binomial_probabilities_manual(n, p):  #Рассчитывает теоретические вероятности биномиального распределения для каждого значения
# probabilities = []
# for k in range(n + 1):
#     prob = binomial_coefficient(n, k) * (p ** k) * ((1 - p) ** (n - k))
#     probabilities.append(prob)
# return probabilities

# def calculate_statistics_manual(data, n, p):  #Рассчитывает теоретические и выборочные статистические характеристики
# expected_value = n * p
# variance = n * p * (1 - p)

# sample_sum = sum(data)
# sample_mean = sample_sum / len(data)
# sample_variance = sum((x - sample_mean) ** 2 for x in data) / len(data)
# sample_median = (sorted(data)[len(data) // 2 - 1] + sorted(data)[len(data) // 2]) / 2 if len(data) % 2 == 0 else sorted(data)[len(data) // 2]
# sample_range = max(data) - min(data)

# return {
#     "Eη": expected_value,   #Мат ожидание
#     "Dη": variance,         #Дисперсия
#     "x̄": sample_mean,       #Выборочное среднее
#     "S^2": sample_variance, #Выборочная дисперсия
#     "Me": sample_median,    #Медиана
#     "R": sample_range,      #Размах
# }

# def display_statistics(statistics):
# # Создаем новое окно для отображения таблицы характеристик
# stats_window = tk.Toplevel(root)
# stats_window.title("Таблица характеристик")
# stats_window.geometry("700x400")  # Увеличенные размеры окна

# # Создаем фрейм для таблицы
# stats_frame = ttk.LabelFrame(stats_window, text="Характеристики", padding=10)
# stats_frame.pack(fill='both', expand=True, padx=10, pady=10)

# # Создаем таблицу для отображения характеристик
# stats_tree = ttk.Treeview(stats_frame, columns=('Parameter', 'Value'), show='headings', height=15)
# stats_tree.heading('Parameter', text='Параметр')
# stats_tree.heading('Value', text='Значение')
# #stats_tree.heading('Difference', text='Разница')
# stats_tree.column('Parameter', width=200, anchor='center')
# stats_tree.column('Value', width=150, anchor='center')
# #stats_tree.column('Difference', width=150, anchor='center')
# stats_tree.pack(fill='both', expand=True)

# # Добавляем строки с характеристиками
# stats_tree.insert('', 'end', values=('Eη (мат. ожидание)', f"{statistics['Eη']:.4f}"))
# stats_tree.insert('', 'end', values=('x̄ (среднее)', f"{statistics['x̄']:.4f}"))
# stats_tree.insert('', 'end', values=('Eη - x̄ ', f"{abs(statistics['Eη'] - statistics['x̄']):.4f}"))
# stats_tree.insert('', 'end', values=('Dη (дисперсия)', f"{statistics['Dη']:.4f}"))
# stats_tree.insert('', 'end', values=('S^2 (выборочная дисперсия)', f"{statistics['S^2']:.4f}"))
# stats_tree.insert('', 'end', values=('Dη - S^2', f"{abs(statistics['Dη'] - statistics['S^2']):.4f}"))
# stats_tree.insert('', 'end', values=('Me (медиана)', f"{statistics['Me']:.4f}"))
# stats_tree.insert('', 'end', values=('R (размах)', f"{statistics['R']:.4f}"))

# # Кнопка закрытия окна
# close_button = ttk.Button(stats_window, text="Закрыть", command=stats_window.destroy)
# close_button.pack(pady=10)

# def display_frequencies_and_deviations(mas_ni, mas_n, theoretical_probs, n,max_diff,xm):
# # Создаем новое окно для отображения таблицы частот и отклонений
# stats_window = tk.Toplevel(root)
# stats_window.title("Таблица частот и отклонений")
# stats_window.geometry("800x500")  # Увеличенные размеры окна

# # Создаем фрейм для таблицы
# stats_frame = ttk.LabelFrame(stats_window, text="Частоты и отклонения", padding=10)
# stats_frame.pack(fill='both', expand=True, padx=10, pady=10)

# # Создаем таблицу для отображения частот и отклонений
# stats_tree = ttk.Treeview(stats_frame, columns=('y_i', 'P_eta_y_i', 'n_i', 'n_i_n', 'abs_diff'),
#                             show='headings', height=15)
# stats_tree.heading('y_i', text='y_i')
# stats_tree.heading('P_eta_y_i', text='P(η=y_i)')
# stats_tree.heading('n_i', text='n_i')
# stats_tree.heading('n_i_n', text='n_i/n')
# stats_tree.heading('abs_diff', text='|n_i/n - P|')

# stats_tree.column('y_i', width=100, anchor='center')
# stats_tree.column('P_eta_y_i', width=150, anchor='center')
# stats_tree.column('n_i', width=100, anchor='center')
# stats_tree.column('n_i_n', width=150, anchor='center')
# stats_tree.column('abs_diff', width=150, anchor='center')
# stats_tree.pack(fill='both', expand=True)

# # Добавляем строки с частотами и отклонениями
# for i in range(n + 1):
#     relative_freq = mas_n[i]
#     theoretical_prob = theoretical_probs[i]
#     abs_diff = abs(relative_freq - theoretical_prob)
#     stats_tree.insert('', 'end', values=(
#         f"{i}", 
#         f"{theoretical_prob:.4f}", 
#         f"{mas_ni[i]}", 
#         f"{relative_freq:.4f}", 
#         f"{abs_diff:.4f}"
#     ))
#     # Добавляем текст под таблицей
# explanation_label = ttk.Label(stats_window, text=(f"Мера расхождения D: {max_diff:.4f} при {xm}"), wraplength=780, justify="center")
# explanation_label.pack(pady=10, padx=10)

# # Кнопка закрытия окна
# close_button = ttk.Button(stats_window, text="Закрыть", command=stats_window.destroy)
# close_button.pack(pady=10)

# #def calculate_max_difference_manual(frequencies, relative_frequencies, theoretical_probs, n):
# #max_diff = 0
# #xn = 0
# #for i in range(n + 1):
#     #if ((relative_frequencies[i] - theoretical_probs[i]) > max_diff):
#     #max_diff = (relative_frequencies[i] - theoretical_probs[i])
#     #xn = i
# ## max_diff = max(abs(relative_frequencies[i] - theoretical_probs[i]) for i in range(n + 1))
# #return max_diff, xn

# def plot_distribution_functions_manual(data, theoretical_probs, n): 
# theoretical_cdf = []
# cumulative = 0
# for prob in theoretical_probs:
#     cumulative += prob
#     theoretical_cdf.append(cumulative)

# sorted_data = sorted(data)
# sample_cdf = []
# for value in range(n + 1):
#     count = sum(1 for x in sorted_data if x <= value)
#     sample_cdf.append(count / len(data))

# max_diff = 0
# xn = 0
# for i in range(n + 1):
#     if (theoretical_cdf[i] - sample_cdf[i]) > max_diff:
#         max_diff = (theoretical_cdf[i] - sample_cdf[i])
#         xn = i

# # Собираем точки для обеих функций
# #theoretical_points = list(zip(range(n + 1), theoretical_cdf))
# #sample_points = list(zip(range(n + 1), sample_cdf))

# plt.step(range(n + 1), theoretical_cdf, label="Теоретическая Fη(x)", where="post")
# plt.step(range(n + 1), sample_cdf, label="Выборочная F̂η(x)", where="post", linestyle="--")
# plt.xlabel("x")
# plt.ylabel("F(x)")
# plt.legend()
# plt.title("Функции распределения")
# plt.grid()
# plt.show()
# return max_diff, xn
# #, theoretical_points, sample_points

# def run_experiment():
# try:
#     n = int(entry_n.get())
#     p = float(entry_p.get())
#     experiments = int(entry_experiments.get())

#     if n <= 0 or not (0 <= p <= 1) or experiments <= 0:
#         raise ValueError("Некорректные данные")

#     mas_y = [i for i in range(n + 1)]
#     mas_ni = [0] * (n + 1)
#     mas_n = [0] * (n + 1)
#     data = []

#     for _ in range(experiments):
#         distorted_count = 0
#         for _ in range(n): #Проверка искажения сообщения
#             if random.random() < p: #генерация случайного числа
#                 distorted_count += 1 #Считает, сколько сообщений искажено(задается случайная величина)
#         mas_ni[distorted_count] += 1 #счётчик сколько раз случайная величина приняла каждое возможное значение
#         data.append(distorted_count)

#     for i in range(len(mas_ni)): #вычисляет относительные частоты каждого значения случайной величины в проведённых экспериментах
#         mas_n[i] = mas_ni[i] / experiments 

#     update_table(mas_y, mas_ni, mas_n)

#     theoretical_probs = theoretical_binomial_probabilities_manual(n, p)
#     max_diff, xn = plot_distribution_functions_manual(data, theoretical_probs, n)
#     #, theoretical_points, sample_points
#     # Печать точек
#     #print("Точки теоретической CDF:")
#     #for x, F in theoretical_points:
#         #print(f"x={x}, F={F:.4f}")

#     #print("\nТочки выборочной CDF:")
#     #for x, F in sample_points:
#         #print(f"x={x}, F={F:.4f}")


#     statistics = calculate_statistics_manual(data, n, p)
#     display_statistics(statistics)
#     display_frequencies_and_deviations(mas_ni,mas_n,theoretical_probs,n,max_diff,xn)
    
#     plot_distribution_functions_manual(data, theoretical_probs, n)
    

# except ValueError:
#     messagebox.showerror("Ошибка ввода", "Проверьте введённые значения:\n"
#                                             "Число сообщений должно быть > 0,\n"
#                                             "Вероятность искажения должна быть в пределах [0, 1],\n"
#                                             "Число экспериментов должно быть > 0.")

# def update_table(mas_y, mas_ni, mas_n):
# for i in tree.get_children():
#     tree.delete(i)

# for i in range(len(mas_y)):
#     tree.insert('', 'end', values=(mas_y[i], mas_ni[i], f"{mas_n[i]:.3f}"))

# root = tk.Tk()
# root.title("Experiment Results: Channel Distortions")
# root.geometry("700x600")

# main_frame = ttk.Frame(root, padding=10)
# main_frame.pack(fill='both', expand=True)

# param_frame = ttk.LabelFrame(main_frame, text="Параметры эксперимента", padding=10)
# param_frame.pack(fill='x', pady=10)

# ttk.Label(param_frame, text='Число сообщений n:').grid(row=0, column=0, sticky='w', pady=5)
# entry_n = ttk.Entry(param_frame)
# entry_n.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

# ttk.Label(param_frame, text='Вероятность искажения p:').grid(row=1, column=0, sticky='w', pady=5)
# entry_p = ttk.Entry(param_frame)
# entry_p.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

# ttk.Label(param_frame, text='Число экспериментов:').grid(row=2, column=0, sticky='w', pady=5)
# entry_experiments = ttk.Entry(param_frame)
# entry_experiments.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

# param_frame.columnconfigure(1, weight=1)

# btn_run = ttk.Button(main_frame, text="Начать вычисления", command=run_experiment)
# btn_run.pack(pady=12)

# results_frame = ttk.LabelFrame(main_frame, text="Результаты эксперимента", padding=10)
# results_frame.pack(fill='both', expand=True)

# tree = ttk.Treeview(results_frame, columns=('Value', 'Occurrences', 'Frequency'), show='headings', height=15)
# tree.heading('Value', text='Значения с.в.')
# tree.heading('Occurrences', text='Число выпадений')
# tree.heading('Frequency', text='Частота')
# tree.column('Value', anchor='center', width=100)
# tree.column('Occurrences', anchor='center', width=150)
# tree.column('Frequency', anchor='center', width=150)
# tree.pack(fill='both', expand=True)

# root.mainloop()
