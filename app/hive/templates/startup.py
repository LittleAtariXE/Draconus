

if __name__ == "__main__":
    {% if MULTIPROCESING_FREEZE %}
    multiprocessing.freeze_support()
    {% endif %}
    WORM = {{WORM_NAME}}()
    WORM.START()